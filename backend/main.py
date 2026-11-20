from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from ml.analyze import analyze

app = FastAPI()

class Review(BaseModel):
    text: str
    rating: Optional[float] = None

class Payload(BaseModel):
    title: Optional[str] = ""
    avg_rating: Optional[float] = None
    reviews: List[Review]

@app.post("/analyze")
def run(p: Payload):
    return analyze([r.dict() for r in p.reviews], p.avg_rating)