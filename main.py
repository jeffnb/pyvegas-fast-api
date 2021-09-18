import asyncio
import csv
import time
from copy import copy
from typing import Optional
from uuid import uuid4, UUID

from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

app = FastAPI()

class Cereal(BaseModel):
    uid: UUID = Field(default_factory=uuid4)
    name: str = Field(max_length=50)
    mfr: str = Field(max_length=1)
    type: str = Field(max_length=1)
    calories: int = Field(ge=0)
    protein: int = Field(ge=0)
    sodium: int = Field(ge=0)
    fiber: float = Field(ge=0)
    carbo: float = Field(ge=-1)
    sugars: int = Field(ge=-1)
    potass: int = Field(ge=-1)
    vitamins: int = Field(ge=0)
    shelf: int = Field(ge=0)
    weight: float = Field(ge=0)
    cups: float = Field(ge=0)
    rating: float = Field(gt=0)

    def normalize(self):
        """
        return a normalized view to 1 cup
        Returns:
        """
        new_numbers = self.copy()
        ratio = 1/new_numbers.cups

        new_numbers.cups = 1
        new_numbers.calories *= ratio
        new_numbers.protein *= ratio
        new_numbers.sodium *= ratio
        new_numbers.fiber *= ratio
        new_numbers.carbo *= ratio
        new_numbers.sugars *= ratio
        new_numbers.potass *= ratio
        new_numbers.vitamins *= ratio

        return new_numbers


# These are just to simulate a data store
cereals = []
def setup():
    with open("cereal.csv", "r") as f:
        reader = csv.DictReader(f)
        for idx, line in enumerate(reader):
            cereals.append(Cereal(**line))


def sleepy():
    print("About to sleep")
    time.sleep(20)
    print("Sleepy time over")


@app.get("/cereals/")
def get_all(background_tasks: BackgroundTasks,
            q: Optional[str] = Query(None, max_length=50, description="Search names"),
            calories: Optional[int] = Query(None, ge=0, description="Calories to match")):

    filtered = copy(cereals)

    if q:
        filtered = [cereal for cereal in filtered if q.lower() in cereal.name.lower()]

    if calories:
        filtered = [cereal for cereal in filtered if cereal.calories == calories]

    background_tasks.add_task(sleepy)
    return filtered


@app.post("/cereals")
def create_new(cereal: Cereal):
    cereals.append(cereal)
    return cereal


@app.get("/cereals/{cereal_id}")
def get_one(cereal_id: UUID, normalize: Optional[bool] = False):
    """
    Get the cereal with the given UUID
    Args:
        cereal_id:
        normalize:
    Returns:
    """
    results = [cereal for cereal in cereals if cereal.uid == cereal_id]

    if not results:
        raise HTTPException(status_code=404, detail="Item not found with that id")

    cereal = results[0]
    if normalize:
        cereal = cereal.normalize()

    return cereal


setup()

