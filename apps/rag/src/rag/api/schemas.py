from pydantic import BaseModel, Field


class IngestResponse(BaseModel):
    chunks_indexed: int


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    k: int = Field(default=3, ge=1, le=20)


class SearchResultSchema(BaseModel):
    text: str
    source: str
    score: float


class SearchResponse(BaseModel):
    results: list[SearchResultSchema]
