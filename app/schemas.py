
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

from pydantic import BaseModel
from datetime import date

class BlogPostCreate(BaseModel):
    title: str
    content: str
    date: date

class BlogPost(BlogPostCreate):
    id: int

    class Config:
        orm_mode = True

