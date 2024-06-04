from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

import models
from database import engine, SessionLocal
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"


# ACCESS_TOKEN_EXPIRE_MINUTES = 30


class CreateUser(BaseModel):
    email: str = Field(min_length=3, max_length=50)
    username: Optional[str]
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=50)
    # is_active: bool


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

models.Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


app = FastAPI()


def get_password_hash(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db):
    user = db.query(models.Users).filter(models.Users.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


# def create_access_token(user_name: str, user_id: int, expires_delta: Optional[timedelta] = None):
#     encode = {'sub': user_name, 'id': user_id}
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=15)
#     encode.update({'exp': expire.timestamp()})  # Use timestamp for exp
#     return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    to_encode = {
        "sub": username,
        "id": user_id,
        "exp": datetime.utcnow() + expires_delta
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        print('token  ------------------------------------->>>>>>>>>>>')
        print(token)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise get_user_exception()

        # Verify if token is expired
        expire = payload.get("exp")
        if expire and datetime.fromtimestamp(expire) < datetime.utcnow():
            raise get_user_exception()

        return {"username": username, "user_id": user_id}
    except JWTError as e:
        print(f"JWTError: {e}")  # Debugging statement
        raise get_user_exception()
    except Exception as e:
        print(f"Error: {e}")  # Debugging statement
        raise get_user_exception()


@app.post('/')
async def create_new_user(create_user: CreateUser, db: Session = Depends(get_db)):
    user = models.Users()
    user.email = create_user.email
    user.username = create_user.username
    user.first_name = create_user.first_name
    user.last_name = create_user.last_name
    hash_password = get_password_hash(create_user.password)
    user.hashed_password = hash_password
    user.is_active = True

    db.add(user)
    db.commit()
    db.refresh(user)  # Ensure the user object is updated

    return user


@app.post('/token')
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise get_token_exception()

    token_expires = timedelta(minutes=30)  # Adjusted to 30 minutes
    token = create_access_token(user.username, user.id, expires_delta=token_expires)
    return {"access_token": token, "token_type": "bearer"}


# Exception handlers
def get_user_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={'WWW-Authenticate': "Bearer"}
    )


def get_token_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={'WWW-Authenticate': "Bearer"}
    )
