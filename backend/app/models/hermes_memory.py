"""Pydantic models for hermes memory data."""

from pydantic import BaseModel, Field


class HermesProfileData(BaseModel):
    """Memory data for a single profile."""
    memory: list[str] = Field(default_factory=list)
    user: list[str] = Field(default_factory=list)


class HermesMemoryResponse(BaseModel):
    """Response for GET /api/hermes-memory."""
    global_data: HermesProfileData = Field(alias="global", default_factory=HermesProfileData)
    profiles: dict[str, HermesProfileData] = Field(default_factory=dict)

    class Config:
        populate_by_name = True
