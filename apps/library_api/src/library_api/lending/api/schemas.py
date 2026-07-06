from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from library_api.shared.validation import normalize_optional_text, normalize_required_text


class MemberCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr

    _normalize_name = field_validator("name")(normalize_required_text)


class MemberUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)

    _normalize_name = field_validator("name")(normalize_optional_text)


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
    book_title: str
    member_id: int
    member_name: str
    loaned_at: datetime
    due_at: datetime
    returned_at: datetime | None
