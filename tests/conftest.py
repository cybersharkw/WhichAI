import os
from pathlib import Path
import subprocess
import sys

import pytest
from fastapi.testclient import TestClient

from backend.config import Settings
from backend.main import create_app

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_alembic(database_url: str, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "alembic", *arguments],
        cwd=PROJECT_ROOT,
        env={**os.environ, "WHICH_DATABASE_URL": database_url},
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )


@pytest.fixture
def database_settings(tmp_path):
    # Apply the real migration, rather than hiding migration issues with create_all.
    database_url = f"sqlite:///{(tmp_path / 'test.db').as_posix()}"
    run_alembic(database_url, "upgrade", "head")
    return Settings(_env_file=None, database_url=database_url)


@pytest.fixture
def client(database_settings):
    with TestClient(create_app(database_settings)) as test_client:
        yield test_client
