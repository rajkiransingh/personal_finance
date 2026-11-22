from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.spendings.expense import Liabilities, LiabilityValue
from backend.schemas.liability_schema import (
    LiabilityTypeCreate,
    LiabilityTypeResponse,
    LiabilityValueCreate,
    LiabilityValueResponse,
    LiabilityValueUpdate,
)
from backend.services.auth import get_data_scope
from backend.services.db_services import get_db
from backend.services.scope import apply_scope, require_owner
from utilities.common.base_fetcher import BaseFetcher

router = APIRouter(prefix="/liabilities", tags=["Liabilities"])

converter = BaseFetcher("liabilities.routes", "liabilities")


def _invalidate_dashboard_cache() -> None:
    """Recompute net worth for every scope after a liability change."""
    try:
        client = converter.redis_client
        for key in client.scan_iter(match="dashboard::*"):
            client.delete(key)
    except Exception as exc:
        converter.logger.warning(f"Dashboard cache invalidation failed: {exc}")


def _with_inr(value: LiabilityValue, liability_type: str | None) -> dict:
    return {
        "id": value.id,
        "liability_id": value.liability_id,
        "value": value.value,
        "currency": value.currency,
        "comment": value.comment,
        "date": value.date,
        "liability_type": liability_type,
        "value_inr": round(
            float(value.value) * converter.get_conversion_rate_against_inr(value.currency), 2
        ),
    }


def _owned_liability(db, liability_id, scope):
    liability = db.query(Liabilities).filter(
        Liabilities.liability_id == liability_id
    ).first()
    if not liability:
        raise HTTPException(status_code=404, detail="Liability type not found")
    require_owner(liability.user_id, scope)
    return liability


@router.get("/types", response_model=List[LiabilityTypeResponse])
def read_liability_types(
    db: Session = Depends(get_db), scope: list[int] = Depends(get_data_scope)
):
    return apply_scope(
        db.query(Liabilities).order_by(Liabilities.liability_type), Liabilities, scope
    ).all()


@router.post("/types", response_model=LiabilityTypeResponse)
def add_liability_type(
    payload: LiabilityTypeCreate,
    db: Session = Depends(get_db),
    scope: list[int] = Depends(get_data_scope),
):
    name = payload.liability_type.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Liability type cannot be empty")
    if not scope:
        raise HTTPException(status_code=403, detail="No personal data scope")

    existing = (
        apply_scope(db.query(Liabilities), Liabilities, scope)
        .filter(func.lower(Liabilities.liability_type) == func.lower(name))
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Liability type already exists")

    row = Liabilities(liability_type=name, user_id=scope[0])
    db.add(row)
    db.commit()
    db.refresh(row)
    _invalidate_dashboard_cache()
    return row


@router.get("", response_model=List[LiabilityValueResponse])
def read_liability_values(
    db: Session = Depends(get_db), scope: list[int] = Depends(get_data_scope)
):
    query = (
        db.query(LiabilityValue, Liabilities.liability_type)
        .join(Liabilities, LiabilityValue.liability_id == Liabilities.liability_id)
    )
    if scope is not None:
        query = query.filter(Liabilities.user_id.in_(scope))
    rows = query.order_by(LiabilityValue.date.desc()).all()
    return [_with_inr(value, name) for value, name in rows]


@router.post("", response_model=LiabilityValueResponse)
def add_liability_value(
    payload: LiabilityValueCreate,
    db: Session = Depends(get_db),
    scope: list[int] = Depends(get_data_scope),
):
    liability = _owned_liability(db, payload.liability_id, scope)

    row = LiabilityValue(
        liability_id=payload.liability_id,
        value=payload.value,
        currency=payload.currency,
        comment=(payload.comment or "").strip(),
        date=payload.date,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    _invalidate_dashboard_cache()
    return _with_inr(row, liability.liability_type)


@router.put("/{value_id}", response_model=LiabilityValueResponse)
def update_liability_value(
    value_id: int,
    payload: LiabilityValueUpdate,
    db: Session = Depends(get_db),
    scope: list[int] = Depends(get_data_scope),
):
    row = db.query(LiabilityValue).filter(LiabilityValue.id == value_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Liability entry not found")
    _owned_liability(db, row.liability_id, scope)

    updates = payload.model_dump(exclude_unset=True)
    if "liability_id" in updates:
        _owned_liability(db, updates["liability_id"], scope)
    for field, value in updates.items():
        if field == "comment":
            value = (value or "").strip()
        setattr(row, field, value)

    db.commit()
    db.refresh(row)
    _invalidate_dashboard_cache()
    liability = db.query(Liabilities).filter(
        Liabilities.liability_id == row.liability_id
    ).first()
    return _with_inr(row, liability.liability_type if liability else None)


@router.delete("/{value_id}")
def delete_liability_value(
    value_id: int,
    db: Session = Depends(get_db),
    scope: list[int] = Depends(get_data_scope),
):
    row = db.query(LiabilityValue).filter(LiabilityValue.id == value_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Liability entry not found")
    _owned_liability(db, row.liability_id, scope)
    db.delete(row)
    db.commit()
    _invalidate_dashboard_cache()
    return {"message": "Liability entry deleted successfully"}
