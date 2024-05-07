from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID
from fastapi import FastAPI, HTTPException, Request, status, Form, Header
from starlette.responses import JSONResponse

app = FastAPI()


class NegativeNumberExceptionHandler(Exception):
    def __init__(self, books_to_return):
        self.books_to_return = books_to_return


class Book(BaseModel):
    id: UUID
    title: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(
        title="description",
        min_length=1,
        max_length=100
    )
    rating: int = Field(gt=-1, lt=101)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "94d48d22-a805-4c4d-aa99-0560d0daa4af",
                "title": "example book title",
                "author": "example book author",
                "description": "example book description",
                "rating": 80,
            }
        }


class BookNoRating(BaseModel):
    id: UUID
    title: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(
        None,
        title="description",
        min_length=1,
        max_length=100
    )


BOOKS = []


@app.exception_handler(NegativeNumberExceptionHandler)
async def negative_number_exception_handler(request: Request, exception: NegativeNumberExceptionHandler):
    return JSONResponse(status_code=477, content={
        "message": f"why do you want {exception.books_to_return} books! you need to read more"})


@app.get('/book/{book_id}')
async def get_book(book_id: UUID):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise raise_item_can_not_be_found_exception()


@app.get('/book/rating/{book_id}', response_model=BookNoRating)
async def get_book_no_rating(book_id: UUID):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise raise_item_can_not_be_found_exception()


@app.delete('/book/{book_id}')
async def delete_book(book_id: UUID):
    counter = 0
    for book in BOOKS:
        counter += 1
        if book.id == book_id:
            del BOOKS[counter - 1]
            return {"message": f"book: {book.id} deleted"}
    raise raise_item_can_not_be_found_exception()


@app.put('/book/{book_id}')
async def get_book(book_id: UUID, book: Book):
    counter = 0
    for book_ in BOOKS:
        counter += 1
        if book_.id == book_id:
            BOOKS[counter - 1] = book
            print(BOOKS[counter - 1])
            return BOOKS[counter - 1]
    raise raise_item_can_not_be_found_exception()


@app.post('/book/login')
async def login(username: str = Form(...), password: str = Form(...)):
    return {'username': username, 'password': password}


@app.get('/')
async def get_all_books(books_to_return: Optional[int] = None):
    if books_to_return and books_to_return < 0:
        raise NegativeNumberExceptionHandler(books_to_return=books_to_return)

    if len(BOOKS) < 1:
        create_book_no_api()

    if books_to_return and len(BOOKS) >= books_to_return > 0:
        i = 0
        new_books = []
        while i < books_to_return:
            new_books.append(BOOKS[i])
            i += 1
        return new_books

    return BOOKS


@app.post('/', response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(book: Book):
    BOOKS.append(book)
    return book


@app.get('/header')
async def read_header(random_header: Optional[str] = Header(None)):
    return {'Random-Header': random_header}


def create_book_no_api():
    book_1 = Book(
        id="3f7b7d94-abcb-4da7-be7c-997b1b453614",
        title="book_1 title",
        author="book_1 author",
        description="book_1 description",
        rating=60,
    )

    book_2 = Book(
        id="e3162da5-e5a2-4eba-863a-4edcae15b86c",
        title="book_2 title",
        author="book_2 author",
        description="book_2 description",
        rating=61,
    )

    book_3 = Book(
        id="b33ce3b4-79f0-4924-b7d1-900474f0a52f",
        title="book_3 title",
        author="book_3 author",
        description="book_3 description",
        rating=62,
    )

    book_4 = Book(
        id="0ca90d5f-7554-4e40-a62c-eac2f2b94b72",
        title="book_4 title",
        author="book_4 author",
        description="book_4 description",
        rating=63,
    )

    BOOKS.append(book_1)
    BOOKS.append(book_2)
    BOOKS.append(book_3)
    BOOKS.append(book_4)


def raise_item_can_not_be_found_exception():
    return HTTPException(
        status_code=404,
        detail="Book not found",
        headers={'X-Header-Error': "Nothing to be seen at UUID"}
    )
