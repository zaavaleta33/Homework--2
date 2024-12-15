# Importing Depends, FastAPI, and HTTPException from the fastapi package
from fastapi import Depends, FastAPI, HTTPException
# Importing BaseModel and EmailStr from pydantic for data validation
from pydantic import BaseModel, EmailStr
# Importing List and Optional from typing to allow typing for lists and optional values
from typing import List, Optional
# Importing create_engine, Column, Integer, and String from sqlalchemy for database interaction
from sqlalchemy import create_engine, Column, Integer, String
# Importing declarative_base from sqlalchemy.ext.declarative to define the base class for ORM models
from sqlalchemy.ext.declarative import declarative_base
# Importing sessionmaker and Session from sqlalchemy.orm for handling database sessions
from sqlalchemy.orm import sessionmaker, Session


# Database connection URL for testing purposes
database_connection_url = "mysql+pymysql://root:Gecko88707@localhost/book_store"
#creates an sqlalchemy engine so that I can connec to the database 
connection_engine = create_engine(database_connection_url, connect_args={"charset": "utf8mb4"})
#session factory that is used to manage database transaction and interacts with database
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=connection_engine)
#creates a base class for my SQLAlchemy models
BaseModelSQLAlchemy = declarative_base()

# SQLAlchemy model representing a book
class BookModel(BaseModelSQLAlchemy):
    # Define the table name in the database
    __tablename__ = "books"
    # Define the book_id column, set as the primary key and indexed for faster lookups
    book_id = Column(Integer, primary_key=True, index=True)
    # Define the book_title column, with a max length of 234 characters and set to NOT NULL
    book_title = Column(String(234), nullable=False)
    # Define the book_author column, with a max length of 234 characters and set to NOT NULL
    book_author = Column(String(234), nullable=False)
    # Define the book_genre column, with a max length of 111 characters and set to NOT NULL
    book_genre = Column(String(111), nullable=False)
    # Define the book_published_year column, set to NOT NULL
    book_published_year = Column(Integer, nullable=False)
    # Define the book_isbn column, with a max length of 15 characters, unique to prevent duplicates, and nullable
    book_isbn = Column(String(15), unique=True, nullable=True)
    # Define the book_publisher column, with a max length of 234 characters and nullable
    book_publisher = Column(String(234), nullable=True)
    # Define the book_page_count column, set to nullable (this means it's optional)
    book_page_count = Column(Integer, nullable=True)
    # Define the book_language column, with a max length of 58 characters and nullable
    book_language = Column(String(58), nullable=True)
    # Define the book_summary column, with a max length of 555 characters and nullable
    book_summary = Column(String(555), nullable=True)
 
# Initialize a FastAPI instance
app = FastAPI()

# Dependency to create and provide a database session
def get_database_session():
    # Creates a new database session to interact with the database
    databaseSession = session_factory()
    try:
        # Yields the database session to be used in a context
        yield databaseSession
    finally:
        #sessions is closed once everything is done
        databaseSession.close()

# Pydantic model for creating a new book
class BookCreateSchema(BaseModel):
    # Title  book 
    book_title: str
    # Author of book 
    book_author: str
    # Genre of book 
    book_genre: str
    # Year the book published 
    book_published_year: int
    # ISBN number of book 
    book_isbn: Optional[str] = None
    # Publisher of book 
    book_publisher: Optional[str] = None
    # Number of pages in book 
    book_number_of_pages: Optional[int] = None
    # Language the book is written in 
    book_language: Optional[str] = None
    # Summary of the book 
    book_summary: Optional[str] = None

# Pydantic model for outputting book details
class BookOutputSchema(BookCreateSchema):
    #Books Identification
    book_id: int

    class Config:
        # Allows Pydantic to work with SQLAlchemy models directly
        orm_mode = True

# Create database tables for the models
BaseModelSQLAlchemy.metadata.create_all(bind=connection_engine)

# Route to retrieve all books
@app.get("/books", response_model=List[BookOutputSchema])
def list_books(databaseSession: Session = Depends(get_database_session)):
    #gets all the books in the database and stores them into book
    books = databaseSession.query(BookModel).all()
    #returns all the books in the database
    return books

# Route to retrieve a specific book by ID
@app.get("/books/{book_id}", response_model=BookOutputSchema)
def retrieve_book(book_id: int, databaseSession: Session = Depends(get_database_session)):
    #finds the first book in the database
    book = databaseSession.query(BookModel).filter(BookModel.book_id == book_id).first()
    if not book:
        #if the book has not been found it will spit out "Book not found"
        raise HTTPException(status_code=404, detail="Book not found")
    #returns the book it has found
    return book

# Route to add a new book
@app.post("/books", response_model=BookOutputSchema)
def add_book(book_data: BookCreateSchema, databaseSession: Session = Depends(get_database_session)):
    #creates a new book
    new_book = BookModel(
        #copies the data into book_title
        book_title=book_data.book_title,
        #copies the data into book_author
        book_author=book_data.book_author,
        #copies the data into book_genre
        book_genre=book_data.book_genre,
        #copies the data into book_published_year
        book_published_year=book_data.book_published_year,
        #copies the data into book_isbn
        book_isbn=book_data.book_isbn,
        #copies the data into book_published_year
        book_publisher=book_data.book_publisher,
        #copies the data into book_number_of_pages
        book_page_count=book_data.book_number_of_pages,
        #copies the data into book_language
        book_language=book_data.book_language,
        #copies the data into book_summary
        book_summary=book_data.book_summary,
    )
    #adds the book object to the session
    databaseSession.add(new_book)
    #commits the changes
    databaseSession.commit()
    #reloads the new_book object from the database 
    databaseSession.refresh(new_book)
    #returns new_book
    return new_book

# Route to modify an existing book
@app.put("/books/{book_id}", response_model=BookOutputSchema)
def modify_book(book_id: int, updated_book_data: BookCreateSchema, databaseSession: Session = Depends(get_database_session)):
    #checks to see if it exists already
    book_exists_already = databasesession.query(bookmodel).filter(bookmodel.book_id == book_id).first()
    #if the book doesn't exists  it will say that the book not found
    if not book_exists_already:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Update the book title with the new title from the updated data
    book_exists_already.book_title = updated_book_data.book_title
    # Update the book author with the new author from the updated data
    book_exists_already.book_author = updated_book_data.book_author
    # Update the book genre with the new genre from the updated data
    book_exists_already.book_genre = updated_book_data.book_genre
    # Update the book published year with the new year from the updated data
    book_exists_already.book_published_year = updated_book_data.book_published_year
    # Update the book ISBN with the new ISBN from the updated data
    book_exists_already.book_isbn = updated_book_data.book_isbn
    # Update the book publisher with the new publisher from the updated data
    book_exists_already.book_publisher = updated_book_data.book_publisher
    # Update the book page count with the new page count from the updated data
    book_exists_already.book_page_count = updated_book_data.book_number_of_pages
    # Update the book language with the new language from the updated data
    book_exists_already.book_language = updated_book_data.book_language
    # Update the book summary with the new summary from the updated data
    book_exists_already.book_summary = updated_book_data.book_summary

    #commits changes 
    databaseSession.commit()
    #refresh
    databaseSession.refresh(book_exists_already)
    #returns book_exists_already
    return book_exists_already

# Route to delete a book
@app.delete("/books/{book_id}")
def remove_book(book_id: int, databaseSession: Session = Depends(get_database_session)):
    #seraches for specific book
    book_to_delete = databaseSession.query(BookModel).filter(BookModel.book_id == book_id).first()
    #if the book has not been found it will say "book not found"
    if not book_to_delete:
        raise HTTPException(status_code=404, detail="Book not found")

    #deletes the book
    databaseSession.delete(book_to_delete)
    #commits the changes
    databaseSession.commit()
    #says that the book has been deleted
    return {"message": f"Book with ID {book_id} has been removed."}

