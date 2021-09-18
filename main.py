import csv
from copy import copy
from uuid import uuid4, UUID

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

class Cereal(BaseModel):
    uid: UUID = Field(default_factory=uuid4)
    name: str
    mfr: str
    type: str
    calories: int
    protein: int
    sodium: int
    fiber: float
    carbo: float
    sugars: int
    potass: int
    vitamins: int
    shelf: int
    weight: float
    cups: float
    rating: float

# These are just to simulate a data store
cereals = []
def setup():
    with open("cereal.csv", "r") as f:
        reader = csv.DictReader(f)
        for line in reader:
            cereals.append(Cereal(**line))


@app.get("/cereals/")
def get_all(q: str = None, calories: int = None):

    filtered = copy(cereals)

    if q:
        filtered = [cereal for cereal in filtered if q.lower() in cereal.name.lower()]

    if calories:
        filtered = [cereal for cereal in filtered if cereal.calories == calories]

    return filtered

@app.get("/cereals/{cereal_id}")
def get_one(cereal_id: UUID):
    """
    Get the cereal with the given UUID
    Args:
        cereal_id:

    Returns:
    """
    results = [cereal for cereal in cereals if cereal.uid == cereal_id]

    if not results:
        raise HTTPException(status_code=404, detail="Item not found with that id")

    return results[0]


setup()

