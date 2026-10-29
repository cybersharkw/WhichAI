from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/")
def root() -> dict[str, str]:
    return {"message": "Hello World"}


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness check; does not test the database connection."""
    return {"status": "ok"}
