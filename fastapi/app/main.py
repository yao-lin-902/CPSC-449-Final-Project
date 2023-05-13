from fastapi import FastAPI
from pymongo import MongoClient
from dotenv import dotenv_values
from .route import book_router, query_router, aggregate_router

config = dotenv_values(".env")
app = FastAPI()


# mongodb handler
@app.on_event("startup")
def start_db():
    app.mongodb = MongoClient(config["DB_URI"])
    app.database = app.mongodb[config["DB_NAME"]]


@app.on_event("shutdown")
def close_db():
    app.mongodb.close()


@app.get("/health")
async def health():
    return {
        "MongoDB": app.mongodb.server_info()["version"],
        "FastAPI": app.version,
    }


app.include_router(book_router, prefix="/book")
app.include_router(query_router, prefix="/search")
app.include_router(aggregate_router, prefix="/aggregate")
