from fastapi import APIRouter

from backend.Model.ModelConfig import ModelConfig

router = APIRouter(tags=["generations"])


@router.post("/generations", response_model=ModelConfig)
def create_ai_model(config: ModelConfig) -> ModelConfig:
    """Keep the existing echo endpoint until a real model adapter is added."""
    return config
