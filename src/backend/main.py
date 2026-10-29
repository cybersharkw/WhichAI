"""Application factory: assemble settings, database and API routers."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import sessionmaker

from backend.api import datasets, generations, health
from backend.config import Settings, get_settings
from backend.db.session import create_database_engine
from backend.services.datasets import DatasetNotFoundError


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings if settings is not None else get_settings()
    engine = create_database_engine(settings.database_url)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            yield
        finally:
            engine.dispose()

    application = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
        telemetry={
            "tracing": False,
            "exclude": lambda scope: scope.get("path") == "/health",
        },
    )
    application.state.settings = settings
    application.state.session_factory = sessionmaker(
        bind=engine, expire_on_commit=False
    )

    @application.exception_handler(DatasetNotFoundError)
    async def dataset_not_found(request: Request, exc: DatasetNotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    application.include_router(health.router)
    application.include_router(generations.router)
    application.include_router(datasets.router)
    return application


app = create_app()
