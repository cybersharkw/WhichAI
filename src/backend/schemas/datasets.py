from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Name = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)
]


class DatasetCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Name
    description: str = Field(default="", max_length=10000)


class DatasetRead(DatasetCreate):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    created_at: datetime
