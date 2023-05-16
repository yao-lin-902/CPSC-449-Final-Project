# Import required modules
from fastapi import FastAPI
from pymongo import MongoClient
from dotenv import dotenv_values
from .route import book_router, query_router, aggregate_router
from motor.motor_asyncio import AsyncIOMotorClient


# Load the environment variables from the '.env' file
config = dotenv_values(".env")

# Create a FastAPI application instance
app = FastAPI()


# Connect to MongoDB database when the application starts
@app.on_event("startup")
async def start_db():
    app.mongodb = AsyncIOMotorClient(config["DB_URI"])
    app.database = app.mongodb[config["DB_NAME"]]
    
    # Create indexes for the 'books' collection
    # creating an index can take some time if the collection is large,
    # and it could potentially block other operations
    # background=True builds the index in the background.
    await app.database["books"].create_index("title", background=True)  # Index for title
    await app.database["books"].create_index("author", background=True)  # Index for author
    await app.database["books"].create_index("price", background=True)  # Index for price


# Disconnect from MongoDB database when the application shuts down
@app.on_event("shutdown")
async def close_db():
    await app.mongodb.close()

# Default route to check the versions of MongoDB and FastAPI
@app.get("/")
async def root():
    return {
        "MongoDB": app.mongodb.server_info()["version"],
        "FastAPI": app.version,
    }

# Include routes for books, search, and aggregate operations
app.include_router(book_router, prefix="/book")
app.include_router(query_router, prefix="/search")
app.include_router(aggregate_router, prefix="/aggregate")
