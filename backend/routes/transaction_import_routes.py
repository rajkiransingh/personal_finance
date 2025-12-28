from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.configurations.bank_config import BANK_MAPPINGS
from backend.schemas.import_schema import ImportConfirmRequest
from backend.services.db_services import get_db
from backend.services.transaction_import_service import (
    preview_csv_import,
    confirm_import_and_learn,
)

router = APIRouter(prefix="/import", tags=["Import"])


@router.get("/banks")
def get_supported_banks():
    return list(BANK_MAPPINGS.keys())


@router.post("/preview")
async def preview_transactions(
    bank_name: str = Form(...), currency: str = Form(...), file: UploadFile = File(...)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Please upload a CSV file."
        )

    content = await file.read()
    try:
        # Returns List[Dict]
        result = preview_csv_import(content, bank_name, currency)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred during preview: {str(e)}"
        )


@router.post("/confirm")
async def confirm_transactions(
    data: ImportConfirmRequest, db: Session = Depends(get_db)
):
    try:
        # data.transactions is List[TransactionPreview] (Pydantic models)
        # Convert to list of dicts for service
        txns_dict = [t.dict() for t in data.transactions]

        result = confirm_import_and_learn(db, data.user_id, txns_dict)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred during confirmation: {str(e)}"
        )
