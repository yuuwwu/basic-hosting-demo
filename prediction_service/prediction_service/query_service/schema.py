from typing import List
from pydantic import BaseModel, Field


class PostQueryRequest(BaseModel):
    query: str = Field(..., description="Input query string to run prediction")
    top_k: int = Field(
        10, description="Number of top categories to return, default to 10"
    )


class PostQueryResponse(BaseModel):
    query: str = Field(..., description="Requested query")
    cats: List[str] = Field([], description="List of predicted categories")
    probas: List[float] = Field(
        [], description="List of predicted probabilities for each category"
    )
