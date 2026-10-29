from pydantic import BaseModel

class ModelConfig(BaseModel):
    name:str
    type:str
    version:float
    systemPrompt:str
    checkpoint:bool
    rag:bool
    agent:bool
    toolItems: list[str]