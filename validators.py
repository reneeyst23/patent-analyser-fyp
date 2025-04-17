from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List

class UploadInput(BaseModel):
    file: Optional[bytes] = Field(None, description="Patent PDF file (optional)")
    serial_number: Optional[str] = Field(None, description="Patent serial number (optional)")

    @validator("serial_number", always=True)
    def check_input(cls, v, values):
        if not v and not values.get("file"):
            raise ValueError("Either file or serial_number must be provided.")
        return v
    
class SimilarPatent(BaseModel):
    patent_id: str
    title: str
    date: str
    inventor: str

class SimilarPatentResponse(BaseModel):
    results: List[SimilarPatent]

# Classification output
class ClassificationResponse(BaseModel):
    triz_labels: List[str]
    eco_topic_labels: List[str]
