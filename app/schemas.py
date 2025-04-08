
from pydantic import BaseModel

class TransactionCreate(BaseModel):
    date: str
    amount: float
    type: str
    category: str
    comment: str

class Transaction(TransactionCreate):
    id: int

    class Config:
        orm_mode = True
