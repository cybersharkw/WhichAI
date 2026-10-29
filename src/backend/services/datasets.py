from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db.models import Dataset, TestCase
from backend.schemas.datasets import DatasetCreate
from backend.schemas.test_cases import TestCaseCreate


class DatasetNotFoundError(Exception):
    def __init__(self, dataset_id: int):
        super().__init__(f"Dataset {dataset_id} not found")


class DatasetService:
    def __init__(self, session: Session):
        self.session = session

    def create_dataset(self, payload: DatasetCreate) -> Dataset:
        dataset = Dataset(**payload.model_dump())
        self.session.add(dataset)
        self.session.commit()
        self.session.refresh(dataset)
        return dataset

    def list_datasets(self, *, offset: int = 0, limit: int = 50) -> list[Dataset]:
        statement = select(Dataset).order_by(Dataset.id).offset(offset).limit(limit)
        return list(self.session.scalars(statement))

    def get_dataset(self, dataset_id: int) -> Dataset:
        dataset = self.session.get(Dataset, dataset_id)
        if dataset is None:
            raise DatasetNotFoundError(dataset_id)
        return dataset

    def create_test_case(self, dataset_id: int, payload: TestCaseCreate) -> TestCase:
        self.get_dataset(dataset_id)
        test_case = TestCase(dataset_id=dataset_id, **payload.model_dump())
        self.session.add(test_case)
        self.session.commit()
        self.session.refresh(test_case)
        return test_case

    def list_test_cases(
        self, dataset_id: int, *, offset: int = 0, limit: int = 50
    ) -> list[TestCase]:
        self.get_dataset(dataset_id)
        statement = (
            select(TestCase)
            .where(TestCase.dataset_id == dataset_id)
            .order_by(TestCase.id)
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.scalars(statement))
