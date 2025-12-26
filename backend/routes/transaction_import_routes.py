from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.services.db_services import get_db
from backend.services.transaction_import_service import process_csv_import
from backend.configurations.bank_config import BANK_MAPPINGS

router = APIRouter(prefix="/import", tags=["Import"])


@router.get("/banks")
def get_supported_banks():
    return list(BANK_MAPPINGS.keys())


@router.post("/transactions")
async def import_transactions(
    user_id: int = Form(...),
    bank_name: str = Form(...),
    currency: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Please upload a CSV file."
        )

    content = await file.read()
    try:
        result = process_csv_import(db, content, bank_name, user_id, currency)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred during import: {str(e)}"
        )
