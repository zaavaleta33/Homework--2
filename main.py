from fastapi import Depends, FastAPI, HTTPException  
from pydantic import BaseModel, EmailStr  
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String  
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker, Session  

#commands to run the program:
# uvicorn main:app --reload
# link to go to  -> http://127.0.0.1:8000/docs

# Database connection URL so that the SQL knows it's me testing it
DATABASE_URL = "mysql://teset:123456789@localhost/student_management_1"

#Creates a data field engine
engine = create_engine(DATABASE_URL, connect_args={"charset": "utf8mb4"})  
#creates a MYSQLAlchemy session factory using the sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  

#creates a database class
Base = declarative_base()  

#class that defines how the MYSQLAlchemy interactes with the database
class Book(Base):
    __tablename__ = "books"  
    id = Column(Integer, primary_key=True, index=True)  
    #the title can not be longer than 234 and it can not be null
    title = Column(String(234), nullable=False)  
    #the author can not bel onger than 234 and it can not be null
    author = Column(String(234), nullable=False)
    # the genre can not be longer than 111 and it can not be null
    genre = Column(String(111), nullable=False)  
    #the published_year can not be null and it has to be an int
    published_year = Column(Integer, nullable=False)
    #the isbn can not be longer than 15, it has to be unique and it can not be null
    isbn = Column(String(15), unique=True, nullable=True)  
    #the publisher can not be longer than 234 and it can be null
    publisher = Column(String(234), nullable=True)        
    #the number of pages can be any number and it can be null
    number_of_pages = Column(Integer, nullable=True)     
    #the language has to be smaller than 58 and it can be null
    language = Column(String(58), nullable=True)        
    #the summary has to be smaller than 55 and it can be null
    summary = Column(String(555), nullable=True)       

#creates a FastAPI instance
app = FastAPI()  

#function that creates a database session that then it provides it to route handler
def get_db():
    #creates a new database
    db = SessionLocal()  
    #alows me to access the database session
    try:
        yield db  
    #no matter what happens, the session will close.
    finally:
        db.close()  


#it's a dynamic model that is used for validating and serializing input data
class BookCreate(BaseModel):
    #defines a field that is a string named title 
    title: str  
    #defines a field that is a string named author
    author: str  
    #defines a field that is a string named genre
    genre: str  
    #defines a field that is an int named published_year
    published_year: int  
    #defines a field that is a string named isbn but also it's optional
    isbn: Optional[str] = None
    #defines a field that is a string named publisher but also it's optional
    publisher: Optional[str] = None
    #defines a field that is an int named number_of_pages but also it's an optional
    number_of_pages: Optional[int] = None
    #defines a field that is a string named language but also it's an optional
    language: Optional[str] = None
    #defines a field that is a string named summary but also it's an optional
    summary: Optional[str] = None

# a pydantic schema used for output data when returning data infomration 
class BookOut(BookCreate):
   
    #defines a field type id of int's
    id: int  
    #used to configure certain behaviors for how Pydantic interactes with the data
    class Config:
        orm_mode = True  

# creating the database tables for all SQLAlchemy models that are associated with the Base class.
Base.metadata.create_all(bind=engine)  

#Fast rout that defines an HTTP GET endpoint at the URL path book
@app.get("/books", response_model=List[BookOut])
# a handler for the HTTP GET request  to the book.
def get_books(db: Session = Depends(get_db)):
    #performes a query on the book table in the database that is stored in book and returns it
    books = db.query(Book).all()  
    return books  
#FastAPI route decorator that defines an HTTP GET 
@app.get("/books/{book_id}", response_model=BookOut)
#route handler that is for the GET 
def get_book(book_id: int, db: Session = Depends(get_db)):
    #get a single book based on the id
    book = db.query(Book).filter(Book.id == book_id).first()  
    #if the book is not found then it will throw a "Book not found" error
    if not book:  
        raise HTTPException(status_code=404, detail="Book not found")
    return book  

#POST route that defines an HTTP GET
@app.post("/books", response_model=BookOut)
#route handler that is for POST
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    #create a new book record that will be in the Database
    db_book = Book(
        title=book.title,  
        author=book.author,  
        genre=book.genre,  
        published_year=book.published_year,  
        isbn=book.isbn,
        publisher=book.publisher,
        number_of_pages=book.number_of_pages,
        language=book.language,
        summary=book.summary,
    )
    #adds db_book into the database
    db.add(db_book)  
    #commits any changes
    db.commit()  
    #reload the state of the object
    db.refresh(db_book)  
    #returns db_book
    return db_book  
#allows the client to update a book that already exists
@app.put("/books/{book_id}", response_model=BookOut)
#updates an existing book
def update_book(book_id: int, updated_book: BookCreate, db: Session = Depends(get_db)):
    #performes a db query to get a specific book from it's id
    db_book = db.query(Book).filter(Book.id == book_id).first()  
    #if the book is not found then it would spit out "Book not found"
    if not db_book:  
        raise HTTPException(status_code=404, detail="Book not found")
    #updates the existing db_book with new title
    db_book.title = updated_book.title  
    #updates the existing db_book with new author
    db_book.author = updated_book.author  
    #updates the existing db_book with new genre
    db_book.genre = updated_book.genre  
    #updates the existing db_book with new published_year
    db_book.published_year = updated_book.published_year  
    #updates the existing db_book with new isbn
    db_book.isbn = updated_book.isbn
    #updates the existing db_book with new published_year
    db_book.publisher = updated_book.publisher
    #updates the existing db_book with new number_of_pages
    db_book.number_of_pages = updated_book.number_of_pages
    #updates the existing db_book with new language
    db_book.language = updated_book.language
    #updates the existing db_book with new summary
    db_book.summary = updated_book.summary
    #commits 
    db.commit()  
    #refreshes db_book
    db.refresh(db_book)  
    #returns db_book
    return db_book  

#Delete route
@app.delete("/books/{book_id}")
#function for deleting book
def delete_book(book_id: int, db: Session = Depends(get_db)):
    #gets a specific book based on the book's ID
    db_book = db.query(Book).filter(Book.id == book_id).first()  
    #if the book is not found then it would spit out "Book not found"
    if not db_book:  
        raise HTTPException(status_code=404, detail="Book not found")
    #deletes a specific book in db_book
    db.delete(db_book)  
    #commits
    db.commit()  
    #says that the book has been deleted
    return {"message": f"Book with ID {book_id} deleted"}  

