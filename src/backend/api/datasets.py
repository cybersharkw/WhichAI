from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from backend.api.dependencies import DatasetServiceDependency
from backend.schemas.datasets import DatasetCreate, DatasetRead
from backend.schemas.test_cases import TestCaseCreate, TestCaseRead

router = APIRouter(prefix="/datasets", tags=["datasets"])
DatasetId = Annotated[int, Path(gt=0)]
Offset = Annotated[int, Query(ge=0)]
Limit = Annotated[int, Query(ge=1, le=100)]


@router.post("", response_model=DatasetRead, status_code=status.HTTP_201_CREATED)
def create_dataset(payload: DatasetCreate, service: DatasetServiceDependency):
    return service.create_dataset(payload)


@router.get("", response_model=list[DatasetRead])
def list_datasets(
    service: DatasetServiceDependency, offset: Offset = 0, limit: Limit = 50
):
    return service.list_datasets(offset=offset, limit=limit)


@router.get("/{dataset_id}", response_model=DatasetRead)
def get_dataset(dataset_id: DatasetId, service: DatasetServiceDependency):
    return service.get_dataset(dataset_id)


@router.post(
    "/{dataset_id}/cases",
    response_model=TestCaseRead,
    status_code=status.HTTP_201_CREATED,
)
def create_test_case(
    dataset_id: DatasetId,
    payload: TestCaseCreate,
    service: DatasetServiceDependency,
):
    return service.create_test_case(dataset_id, payload)


@router.get("/{dataset_id}/cases", response_model=list[TestCaseRead])
def list_test_cases(
    dataset_id: DatasetId,
    service: DatasetServiceDependency,
    offset: Offset = 0,
    limit: Limit = 50,
):
    return service.list_test_cases(dataset_id, offset=offset, limit=limit)
