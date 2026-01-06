from sqlalchemy.orm import Session
from backend.models.investments.protected_instrument import ProtectedInstrument
from backend.schemas.protected_instrument_schema import (
    ProtectedInstrumentCreate,
    ProtectedInstrumentUpdate,
)


def get_all_protected_instruments(db: Session):
    return db.query(ProtectedInstrument).all()


def get_protected_instruments_by_user(db: Session, user_id: int):
    return (
        db.query(ProtectedInstrument)
        .filter(ProtectedInstrument.user_id == user_id)
        .all()
    )


def get_protected_instrument(db: Session, instrument_id: int):
    return (
        db.query(ProtectedInstrument)
        .filter(ProtectedInstrument.id == instrument_id)
        .first()
    )


def create_protected_instrument(db: Session, instrument: ProtectedInstrumentCreate):
    db_instrument = ProtectedInstrument(
        user_id=instrument.user_id,
        name=instrument.name,
        provider=instrument.provider,
        category=instrument.category,
        frequency=instrument.frequency,
        contribution=instrument.contribution,
        start_date=instrument.start_date,
        maturity_date=instrument.maturity_date,
        guaranteed_amount=instrument.guaranteed_amount,
        notes=instrument.notes,
    )
    db.add(db_instrument)
    db.commit()
    db.refresh(db_instrument)
    return db_instrument


def update_protected_instrument(
    db: Session, instrument_id: int, instrument_update: ProtectedInstrumentUpdate
):
    db_instrument = get_protected_instrument(db, instrument_id)
    if not db_instrument:
        return None

    update_data = instrument_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_instrument, key, value)

    db.commit()
    db.refresh(db_instrument)
    return db_instrument


def delete_protected_instrument(db: Session, instrument_id: int):
    db_instrument = get_protected_instrument(db, instrument_id)
    if not db_instrument:
        return None

    db.delete(db_instrument)
    db.commit()
    return db_instrument
