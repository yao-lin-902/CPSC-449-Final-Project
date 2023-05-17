# CPSC-499-Final-Project

Team Members:
Yao Lin
Arish Imam 
Karnikaa Velumani 



Book Store API

This project is an API for a book store, built with FastAPI and MongoDB.

Prerequisites:
Python 3.7 or higher
MongoDB (either locally or a cloud instance like MongoDB Atlas)

Setup
1. Open a terminal and navigate to the fastapi directory of project.

2. Create a virtual environment: 
python3 -m venv env

3. Activate the virtual environment:
Windows: .\env\Scripts\activate
Unix/MacOS: source env/bin/activate

4. Install the requirements:
pip install -r requirements.txt

5. Set up MongoDB:
- You can set up a local MongoDB server or use a MongoDB cloud service like MongoDB Atlas.
- If you're using MongoDB Atlas, make sure to whitelist your IP address and create a user for the database.

6. Create and configure the .env file:
- Ensure you are in fastapi directory, create a file named '.env'
- In this file, specify the MongoDB URI and the database name, like this:
  DB_URI=mongodb+srv://username:password@cluster...
  DB_NAME=your_database_name
- Replace the URI and the database name with your actual MongoDB URI and the name of your database.


Running the API:
1. Ensure you are in fastapi directory.
2. Start the FastAPI server and enter the following into the terminal:
uvicorn app.main:app --reload 
The --reload flag enables hot reloading, which means the server will automatically update whenever you make changes to the code.
3. Open the API in your browser:
- You can now access the API at http://127.0.0.1:8000
- To see the interactive API documentation, navigate to http://127.0.0.1:8000/docs


API Endpoints:
- GET /books: Retrieves a list of all books in the store.
- GET /books/{book_id}: Retrieves a specific book by ID.
- POST /books: Adds a new book to the store.
- PUT /books/{book_id}: Updates an existing book by ID.
- DELETE /books/{book_id}: Deletes a book from the store by ID.
- GET /search?title={}&author={}&min_price={}&max_price={}: Searches for books by title, author, and price range.
