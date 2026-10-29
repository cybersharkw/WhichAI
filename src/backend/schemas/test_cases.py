from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

from backend.schemas.datasets import Name

Criterion = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class TestCaseCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Name
    input: str = Field(min_length=1)
    reference_answer: str = Field(min_length=1)
    evaluation_criteria: list[Criterion] = Field(default_factory=list)

    @field_validator("input", "reference_answer")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Must contain non-whitespace characters")
        # Keep original prompt whitespace: formatting may affect model behavior.
        return value


class TestCaseRead(TestCaseCreate):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    dataset_id: int
    created_at: datetime
