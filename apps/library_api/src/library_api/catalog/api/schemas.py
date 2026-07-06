from pydantic import BaseModel, ConfigDict, Field, field_validator

from library_api.shared.validation import normalize_optional_text, normalize_required_text


class AuthorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    bio: str | None = Field(default=None, max_length=2000)

    _normalize_name = field_validator("name")(normalize_required_text)
    _normalize_bio = field_validator("bio")(normalize_optional_text)


class AuthorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    bio: str | None = Field(default=None, max_length=2000)

    _normalize_name = field_validator("name")(normalize_optional_text)
    _normalize_bio = field_validator("bio")(normalize_optional_text)


class AuthorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    bio: str | None


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    isbn: str = Field(min_length=1, max_length=20)
    category: str = Field(min_length=1, max_length=100)
    author_id: int
    total_copies: int = Field(default=1, ge=1)

    _normalize_title = field_validator("title")(normalize_required_text)
    _normalize_isbn = field_validator("isbn")(normalize_required_text)
    _normalize_category = field_validator("category")(normalize_required_text)


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    total_copies: int | None = Field(default=None, ge=1)

    _normalize_title = field_validator("title")(normalize_optional_text)
    _normalize_category = field_validator("category")(normalize_optional_text)


class BookRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    isbn: str
    category: str
    author_id: int
    author_name: str
    total_copies: int
    available_copies: int
