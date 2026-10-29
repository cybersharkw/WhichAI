from pydantic import BaseModel

class GenerationResult(BaseModel):
    response:str
    runTimeUsed:float
    validationResult:str
    validationSummary:str