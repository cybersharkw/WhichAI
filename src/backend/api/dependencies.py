from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from backend.services.datasets import DatasetService


def get_session(request: Request) -> Iterator[Session]:
    # A separate session per request. Closing rolls back unfinished transactions.
    with request.app.state.session_factory() as session:
        yield session


def get_dataset_service(
    session: Annotated[Session, Depends(get_session)],
) -> DatasetService:
    return DatasetService(session)


DatasetServiceDependency = Annotated[DatasetService, Depends(get_dataset_service)]
