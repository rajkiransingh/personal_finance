from typing import List, Optional
from pydantic import BaseModel


class TransactionPreview(BaseModel):
    date: str
    description: str
    amount: float
    currency: str
    type: str  # 'income' or 'expense'
    category_id: Optional[int] = None
    source_id: Optional[int] = None
    learn_keyword: Optional[str] = (
        None  # If user modified this, pass the keyword to learn
    )


class ImportConfirmRequest(BaseModel):
    user_id: int
    transactions: List[TransactionPreview]
