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
from backend.services.db_services import get_db
from utilities.common.base_fetcher import BaseFetcher

router = APIRouter(prefix="/liabilities", tags=["Liabilities"])

converter = BaseFetcher("liabilities.routes", "liabilities")


def _invalidate_dashboard_cache() -> None:
    """Make the dashboard recompute net worth after a liability change."""
    try:
        converter.redis_client.delete("dashboard::SUMMARY")
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


@router.get("/types", response_model=List[LiabilityTypeResponse])
def read_liability_types(db: Session = Depends(get_db)):
    return db.query(Liabilities).order_by(Liabilities.liability_type).all()


@router.post("/types", response_model=LiabilityTypeResponse)
def add_liability_type(payload: LiabilityTypeCreate, db: Session = Depends(get_db)):
    name = payload.liability_type.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Liability type cannot be empty")

    existing = (
        db.query(Liabilities)
        .filter(func.lower(Liabilities.liability_type) == func.lower(name))
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Liability type already exists")

    row = Liabilities(liability_type=name)
    db.add(row)
    db.commit()
    db.refresh(row)
    _invalidate_dashboard_cache()
    return row


@router.get("", response_model=List[LiabilityValueResponse])
def read_liability_values(db: Session = Depends(get_db)):
    rows = (
        db.query(LiabilityValue, Liabilities.liability_type)
        .join(Liabilities, LiabilityValue.liability_id == Liabilities.liability_id)
        .order_by(LiabilityValue.date.desc())
        .all()
    )
    return [_with_inr(value, name) for value, name in rows]


@router.post("", response_model=LiabilityValueResponse)
def add_liability_value(payload: LiabilityValueCreate, db: Session = Depends(get_db)):
    liability = db.query(Liabilities).filter(
        Liabilities.liability_id == payload.liability_id
    ).first()
    if not liability:
        raise HTTPException(status_code=404, detail="Liability type not found")

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
    value_id: int, payload: LiabilityValueUpdate, db: Session = Depends(get_db)
):
    row = db.query(LiabilityValue).filter(LiabilityValue.id == value_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Liability entry not found")

    updates = payload.model_dump(exclude_unset=True)
    if "liability_id" in updates:
        liability = db.query(Liabilities).filter(
            Liabilities.liability_id == updates["liability_id"]
        ).first()
        if not liability:
            raise HTTPException(status_code=404, detail="Liability type not found")
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
def delete_liability_value(value_id: int, db: Session = Depends(get_db)):
    row = db.query(LiabilityValue).filter(LiabilityValue.id == value_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Liability entry not found")
    db.delete(row)
    db.commit()
    _invalidate_dashboard_cache()
    return {"message": "Liability entry deleted successfully"}
