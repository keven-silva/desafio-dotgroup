from pydantic import BaseModel, Field


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    author: str = Field(min_length=1, max_length=255)


class BookRead(BookCreate):
    id: int

    model_config = {"from_attributes": True}


class AskRequest(BaseModel):
    question: str = Field(min_length=3)


class AskResponse(BaseModel):
    answer: str


class IngestRequest(BaseModel):
    source: str = Field(min_length=3)
    content: str = Field(min_length=10)


class IngestResponse(BaseModel):
    id: int
    dimensions: int
