from fastapi import APIRouter, Request, Body, status, HTTPException, Response, Depends
from fastapi.encoders import jsonable_encoder
from typing import List
from .model import Book, BookUpdate, BookSearch

# Define the routes for the FastAPI application
# Each route corresponds to a specific HTTP method and URI
# and is associated with a function that handles requests to that URI

book_router = APIRouter()
query_router = APIRouter()
aggregate_router = APIRouter()

# Book router contains routes related to book operations
@book_router.get("/", response_model=List[Book])
async def get_all_books(request: Request):
    books = await request.app.database["books"].find().to_list(100)
    return books


@book_router.get("/{id}", response_model=Book)
async def get_book(id: str, request: Request):
    book = await request.app.database["books"].find_one({"_id": id})
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return book


@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book)
async def create_book(request: Request, book: Book = Body(...)):
    book = jsonable_encoder(book)
    new_book = await request.app.database["books"].insert_one(book)
    book = await request.app.database["books"].find_one({"_id": new_book.inserted_id})
    return book


@book_router.delete("/{id}")
async def delete_book(id: str, request: Request, response: Response):
    delete_result = await request.app.database["books"].delete_one({"_id": id})
    if delete_result.deleted_count:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@book_router.put("/{id}", response_model=Book)
async def update_book(id: str, request: Request, book: BookUpdate = Body(...)):
    book = dict(filter(lambda v: v[1] != None, jsonable_encoder(book).items()))
    updated_book = await request.app.database["books"].find_one_and_update(
        {"_id": id}, {"$set": book}
    )
    if updated_book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    book = await request.app.database["books"].find_one({"_id": id})
    return book


# Query router contains routes related to search operations
# Operators 
@query_router.get("/", response_model=List[Book])
async def search_book(request: Request, search: BookSearch = Depends()):
    search = dict(filter(lambda v: v[1] != None, jsonable_encoder(search).items()))
    if "max_price" in search:
        search["price"] = {"$lte": search["max_price"], "$gte": search["min_price"]}
        search.pop("max_price")
        search.pop("min_price")

    books = await request.app.database["books"].find(search).to_list(100)
    return books


# Aggregate router contains routes related to aggregation operations

# Route to get total number of books in the stock
@aggregate_router.get("/count", response_model=int)
async def get_total_number_of_books(request: Request):
    pipeline = [
        {"$group": {"_id": "null", "count": {"$sum": "$stock"}}},
        {"$project": {"_id": 0, "count": 1}},
    ]
    count = await request.app.database["books"].aggregate(pipeline).to_list(None)
    count = count[0]["count"]
    return count

# Route to get best selling books
@aggregate_router.get("/best-selling", response_model=List[Book])
async def get_best_selling_books(request: Request):
    pipeline = [
        {
            "$group": {
                "_id": "$title",
                "stock": {"$sum": "$stock"},
                "book": {"$first": "$$ROOT"},
            }
        },
        {"$sort": {"stock": -1}},
        {"$limit": 5},
        {"$replaceRoot": {"newRoot": "$book"}},
    ]
    books = await request.app.database["books"].aggregate(pipeline).to_list(None)
    return books

# Route to get the most prolific authors
@aggregate_router.get("/prolific-author", response_model=List[str])
async def get_most_prolific_authors(request: Request):
    pipeline = [
        {"$group": {"_id": "$author", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5},
        {"$project": {"_id": 0, "author": "$_id"}},
    ]
    authors = await request.app.database["books"].aggregate(pipeline).to_list(None)
    authors = [a["author"] for a in authors]
    return authors

