from pydantic import BaseModel, Field
from typing import List


class StatusMessage(BaseModel):
    subapps: List[str] = Field(..., description="Mounted Sub-Applications")
    api_state: str = Field(..., description="The state of the API service")


class StatusResponse(BaseModel):
    response: StatusMessage = Field(..., description="Endpoint status")


class DefaultErrorResponse(BaseModel):
    httpStatusCode: int = Field(
        ..., description="HTTP status code (4xx client, 5xx server)"
    )
    httpMessage: str = Field(
        ..., description="HTTP error message (BAD_REQUEST, FORBIDDEN, etc)"
    )
    description: str = Field(..., description="Human readable description of the error")
    api_state: str = Field(None, description="The state of the API service")
    details: str = Field(None, description="Error details")


class DefaultBadRequest(BaseModel):
    error: DefaultErrorResponse = Field(
        ..., description="Object containing error information"
    )
