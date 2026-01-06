from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.schemas.protected_instrument_schema import (
    ProtectedInstrumentCreate,
    ProtectedInstrumentUpdate,
    ProtectedInstrumentResponse,
)
from backend.services.db_services import get_db
from backend.services.protected_instrument_service import (
    get_all_protected_instruments,
    get_protected_instruments_by_user,
    get_protected_instrument,
    create_protected_instrument,
    update_protected_instrument,
    delete_protected_instrument,
)
from backend.services.user_services import get_user

router = APIRouter(prefix="/protected-instruments", tags=["Protected Instruments"])


@router.get("", response_model=List[ProtectedInstrumentResponse])
def read_all_protected_instruments(db: Session = Depends(get_db)):
    return get_all_protected_instruments(db)


@router.get("/user/{user_id}", response_model=List[ProtectedInstrumentResponse])
def read_protected_instruments_by_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    instruments = get_protected_instruments_by_user(db, user_id)
    return instruments


@router.get("/{instrument_id}", response_model=ProtectedInstrumentResponse)
def read_protected_instrument(instrument_id: int, db: Session = Depends(get_db)):
    instrument = get_protected_instrument(db, instrument_id)
    if not instrument:
        raise HTTPException(status_code=404, detail="Protected Instrument not found")
    return instrument


@router.post("", response_model=ProtectedInstrumentResponse)
def add_protected_instrument(
    instrument_data: ProtectedInstrumentCreate, db: Session = Depends(get_db)
):
    return create_protected_instrument(db, instrument_data)


@router.put("/{instrument_id}", response_model=ProtectedInstrumentResponse)
def modify_protected_instrument(
    instrument_id: int,
    instrument_data: ProtectedInstrumentUpdate,
    db: Session = Depends(get_db),
):
    updated_instrument = update_protected_instrument(db, instrument_id, instrument_data)
    if not updated_instrument:
        raise HTTPException(status_code=404, detail="Protected Instrument not found")
    return updated_instrument


@router.delete("/{instrument_id}")
def remove_protected_instrument(instrument_id: int, db: Session = Depends(get_db)):
    deleted_instrument = delete_protected_instrument(db, instrument_id)
    if not deleted_instrument:
        raise HTTPException(status_code=404, detail="Protected Instrument not found")
    return {"message": "Protected Instrument deleted successfully"}
