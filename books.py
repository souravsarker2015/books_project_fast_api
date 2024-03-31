# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="127.0.0.1", port=8000)

from enum import Enum
from typing import Optional

from fastapi import FastAPI

app = FastAPI()

books = {
    "book_1": {
        "title": "Book 1 Title",
        "author": "Author 1"
    },
    "book_2": {
        "title": "Book 2 Title",
        "author": "Author 2"
    },
    "book_3": {
        "title": "Book 3 Title",
        "author": "Author 3"
    }
}


# # Example usage:
# print("Title of book 1:", books["book_1"]["title"])
# print("Author of book 2:", books["book_2"]["author"])


@app.get('/')
async def get_all_books():
    return books


@app.post('/')
async def create_book(book_title, book_author):
    current_book_id = 0
    for book in books:
        x = int(book.split('_')[-1])
        if x > current_book_id:
            current_book_id = x
    books[f'book_{current_book_id + 1}'] = {"title": book_title, "author": book_author}
    print(books)
    return books[f'book_{current_book_id + 1}']


@app.get('/exclude_book')
async def exclude_specific_book(skip_book: Optional[str] = None):  # Default parameter is book_1 in swagger
    # async def exclude_specific_book(skip_book: str = "book_1"):  # Default parameter is book_1 in swagger
    # async def exclude_specific_book(skip_book: str): # Must give the parameter in swagger
    if skip_book:
        new_books = books.copy()
        del new_books[skip_book]
        return new_books
    return books


@app.get('/{book_name}')
async def get_book(book_name: str):
    return books[book_name]


@app.put('/{book_name}')
async def update_book(book_name: str, book_title: str, book_author: str):
    update_info = {'title': book_title, 'author': book_author}
    books[book_name] = update_info
    print(books)
    return books[book_name]


@app.delete('/{book_name}')
async def delete_book(book_name: str):
    del books[book_name]
    print(books)
    return {"status": 200, "message": f"Book:{book_name} deleted"}


@app.get('/books/{title}')
async def read_book(title):
    return {"title": title}


@app.get('/book_id/{book_id}')
async def read_book_id(book_id: int):
    return {"book_id": book_id}


class DirectionName(str, Enum):
    north = "north"
    south = "south"
    east = "east"
    west = "west"


@app.get("/direction/{direction_name}")
async def read_direction(direction_name: DirectionName):
    return {"direction_name": direction_name, 'sub': "up"}
