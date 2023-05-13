from fastapi import APIRouter, Request, Body, status, HTTPException, Response, Depends
from fastapi.encoders import jsonable_encoder
from typing import List
from .model import Book, BookUpdate, BookSearch

book_router = APIRouter()
query_router = APIRouter()
aggregate_router = APIRouter()


@book_router.get("/", response_model=List[Book])
async def get_all_books(request: Request):
    books = list(request.app.database["books"].find(limit=100))
    return books


@book_router.get("/{id}", response_model=Book)
async def get_book(id: str, request: Request):
    book = request.app.database["books"].find_one({"_id": id})
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return book


@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book)
async def create_book(request: Request, book: Book = Body(...)):
    book = jsonable_encoder(book)
    book = request.app.database["books"].insert_one(book)
    book = request.app.database["books"].find_one({"_id": book.inserted_id})
    return book


@book_router.delete("/{id}")
async def delete_book(id: str, request: Request, response: Response):
    if request.app.database["books"].delete_one({"_id": id}).deleted_count:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@book_router.put("/{id}", response_model=Book)
async def update_book(id: str, request: Request, book: BookUpdate = Body(...)):
    book = dict(filter(lambda v: v[1] != None, jsonable_encoder(book).items()))
    book = request.app.database["books"].find_one_and_update(
        {"_id": id}, {"$set": book}
    )
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    book = request.app.database["books"].find_one({"_id": id})
    return book


@query_router.get("/", response_model=List[Book])
async def search_book(request: Request, search: BookSearch = Depends()):
    search = dict(filter(lambda v: v[1] != None, jsonable_encoder(search).items()))
    if "max_price" in search:
        search["price"] = {"$lte": search["max_price"], "$gte": search["min_price"]}
        search.pop("max_price")
        search.pop("min_price")

    books = list(request.app.database["books"].find(search, limit=100))
    return books


@aggregate_router.get("/count", response_model=int)
async def get_total_number_of_books(request: Request):
    pipeline = [
        {"$group": {"_id": "null", "count": {"$sum": "$stock"}}},
        {"$project": {"_id": 0, "count": 1}},
    ]
    count = list(request.app.database["books"].aggregate(pipeline))
    count = count[0]["count"]
    return count


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
    books = list(request.app.database["books"].aggregate(pipeline))
    return books


@aggregate_router.get("/prolific-author", response_model=List[str])
async def get_most_prolific_authors(request: Request):
    pipeline = [
        {"$group": {"_id": "$author", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5},
        {"$project": {"_id": 0, "author": "$_id"}},
    ]
    author = list(request.app.database["books"].aggregate(pipeline))
    author = [a["author"] for a in author]
    return author
