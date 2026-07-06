from pydantic import BaseModel, ConfigDict, Field


class AuthorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    bio: str | None = Field(default=None, max_length=2000)


class AuthorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    bio: str | None = Field(default=None, max_length=2000)


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


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    total_copies: int | None = Field(default=None, ge=1)


class BookRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    isbn: str
    category: str
    author_id: int
    total_copies: int
    available_copies: int
