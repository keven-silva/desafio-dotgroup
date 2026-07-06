from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class MemberCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr


class MemberUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)


class MemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str


class LoanCreate(BaseModel):
    book_id: int
    member_id: int


class LoanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    book_id: int
    member_id: int
    loaned_at: datetime
    due_at: datetime
    returned_at: datetime | None
