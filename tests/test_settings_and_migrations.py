import pytest
from pydantic import ValidationError
from sqlalchemy import inspect

from conftest import run_alembic
from backend.config import Settings
from backend.db.session import create_database_engine


def test_environment_overrides_dotenv(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("WHICH_APP_NAME=From dotenv\nWHICH_PORT=8100\n", encoding="utf-8")
    monkeypatch.delenv("WHICH_APP_NAME", raising=False)
    monkeypatch.setenv("WHICH_PORT", "8200")
    settings = Settings(_env_file=env_file)
    assert settings.app_name == "From dotenv"
    assert settings.port == 8200
    with pytest.raises(ValidationError):
        Settings(_env_file=None, port=0)


def test_migration_matches_models_and_can_be_reapplied(database_settings):
    database_url = database_settings.database_url
    run_alembic(database_url, "check")
    run_alembic(database_url, "downgrade", "base")
    engine = create_database_engine(database_url)
    try:
        assert "datasets" not in inspect(engine).get_table_names()
        assert "test_cases" not in inspect(engine).get_table_names()
    finally:
        engine.dispose()
    run_alembic(database_url, "upgrade", "head")
    engine = create_database_engine(database_url)
    try:
        assert {"datasets", "test_cases"} <= set(inspect(engine).get_table_names())
        with engine.connect() as connection:
            assert connection.exec_driver_sql("PRAGMA foreign_keys").scalar_one() == 1
    finally:
        engine.dispose()
