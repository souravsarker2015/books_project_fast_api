# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="127.0.0.1", port=8000)

from enum import Enum

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


@app.get('/books/{title}')
async def read_books(title):
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
