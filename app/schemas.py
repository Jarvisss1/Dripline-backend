from pydantic import BaseModel, Field
from typing import List, Dict, Any

class ClothingItemSchema(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    image_url: str
    category: str
    tags: Dict[str, Any]
    embedding: List[float]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            "id": str
        }

class RecommendationRequest(BaseModel):
    input_item_id: str
    filters: dict

class RecommendationResponse(BaseModel):
    item: ClothingItemSchema
    compatibility_score: float
