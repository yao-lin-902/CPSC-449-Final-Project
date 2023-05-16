
from pydantic import BaseModel, Field, validator
from fastapi import HTTPException
from typing import Optional
from uuid import uuid4


# Define pydantic data models for a book, book updates, and book search
# These models will be used for validating and deserializing input data
class Book(BaseModel):
    id: str = Field(default_factory=uuid4, alias="_id")
    title: str = Field(...)
    author: str = Field(...)
    description: str = Field(...)
    price: float = Field(...)
    stock: int = Field(...)

    class Config:
        allow_population_by_field_name = True


class BookUpdate(BaseModel):
    title: Optional[str]
    author: Optional[str]
    description: Optional[str]
    price: Optional[float]
    stock: Optional[int]


class BookSearch(BaseModel):
    title: Optional[str]
    author: Optional[str]
    min_price: Optional[float]
    max_price: Optional[float]


    # Validator to check if max price is greater than min price
    @validator("max_price", pre=True)
    def check_price(cls, v, values):
        if values.get("min_price"):
            if v is None:
                raise HTTPException(422, "Missing max price")
            elif values.get("min_price") > v:
                raise HTTPException(422, "Invalid price range")
        elif v and not values.get("min_price"):
            values["min_price"] = 0.0
        return v
