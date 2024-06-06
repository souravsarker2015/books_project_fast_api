import sys

import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from TodoApplicationWithRoutes.routes.auth import get_current_user, get_user_exception

from fastapi import Depends, HTTPException, APIRouter
from TodoApplicationWithRoutes import models
from TodoApplicationWithRoutes.database import engine, SessionLocal

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={404: {'description': 'not found'}}
)

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class ToDo(BaseModel):
    title: str = Field(min_length=1)
    description: Optional[str] = Field(
        title="description",
        min_length=1,
        max_length=100
    )
    priority: int = Field(gt=0, lt=11)
    complete: bool

    class Config:
        json_schema_extra = {
            "example": {
                "title": "example todo1 title",
                "description": "example todo1 description",
                "priority": 10,
                "complete": False,
            }
        }


@router.get('/user')
async def read_all_by_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise get_user_exception()

    return db.query(models.Todos).filter(models.Todos.owner_id == user.get('user_id')).all()


@router.post('/')
async def create_todo(
        todo: ToDo,
        user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)):
    if not user:
        raise get_user_exception()

    todo_model = models.Todos()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
    todo_model.owner_id = user.get('user_id')

    db.add(todo_model)
    db.commit()

    return successful_response(201)


@router.put('/{todo_id}')
async def update_todo(
        todo_id: int,
        todo: ToDo,
        user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)):
    if not user:
        raise get_user_exception()

    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(
        models.Todos.owner_id == user.get('user_id')).first()

    if todo_model is None:
        raise raise_item_can_not_be_found_exception()

    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
    db.add(todo_model)
    db.commit()

    return successful_response(200)


@router.delete('/{todo_id}')
async def delete_todo(
        todo_id: int,
        user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)):
    if not user:
        raise get_user_exception()

    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(
        models.Todos.owner_id == user.get('user_id')).first()

    if todo_model is None:
        raise raise_item_can_not_be_found_exception()

    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()

    return successful_response(200)


@router.get('/')
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Todos).all()


@router.get('/{todo_id}')
async def read_one(todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise get_user_exception()

    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(
        models.Todos.owner_id == user.get('user_id')).first()
    # todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_model:
        return todo_model
    raise raise_item_can_not_be_found_exception()


def successful_response(status=200):
    return {
        "status": status,
        "transaction": "Successful"
    }


def raise_item_can_not_be_found_exception():
    return HTTPException(
        status_code=404,
        detail="Todo not found",
        headers={'X-Header-Error': "Nothing to be seen at UUID"}
    )
