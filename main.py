from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from typing import List,Annotated
import crud
import models
import schemas
from pydantic import BaseModel
from database import SessionLocal, engine
from services import create_default_categories_for_user
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import hash_pwd
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone

SECRET_KEY = "fde4d14c2f92c624229f5938f9ad56fd9a1c43d3c53f1880ffa82c39f24736fd"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:8000",
    "http://localhost:58857",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
class Token(BaseModel):
    access_token: str
    token_type: str
class TokenData(BaseModel):
    username: str | None = None

class UserLogin(BaseModel):
    email: str
    password: str


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db:Session=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db:Session=Depends(get_db)
) -> Token:
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@app.get("/users/me")
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user



@app.post("/users/signup", response_model=schemas.User)
def create_user(new_user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=new_user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    created_user = crud.create_user(db, user=new_user)
    #기본 카테고리 추가
    create_default_categories_for_user(db, user_id=created_user.id)
    crud.create_budget(db,user_id= created_user.id)
    return created_user

@app.post("/users/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = crud.authenticate_user(db, user.email, user.password)
    if db_user:
        return {"id": db_user.id, "username": db_user.username}
    else:
        raise HTTPException(status_code=401, detail="Invalid email or password")

@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/category/add", response_model=schemas.Category)
def create_category_for_user(user_id: int,new_category:schemas.CategoryCreate, db:Session=Depends(get_db)):
    existing_category = crud.get_category_by_name(db, category_name=new_category.name)
    if existing_category:
        raise HTTPException(status_code=400, detail="Category already exist")
    return crud.create_category(db, category=new_category, user_id=user_id)

@app.get("/category/categories/", response_model=List[schemas.Category])
def read_categories(user_id: int,skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    categories = crud.get_categories_by_id(db=db, skip = skip, limit=limit,user_id=user_id)
    return categories

@app.delete("/category/del/one")
def remove_category(user_id:int, category_id: int, db: Session = Depends(get_db)):
    return crud.delete_category(db=db, category_id=category_id, user_id=user_id)

@app.get("/consume.history", response_model=List[schemas.ConsumeHist])
def read_consume_history(user_id: int,db:Session=Depends(get_db)):
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    consume_hist_list = crud.get_consume_history_by_user_id(db,user_id=user_id)
    if not consume_hist_list:
        raise HTTPException(status_code=404, detail="History not found")
    return consume_hist_list

@app.post("/consume.history/add/new_history")
def create_consume_history(user_id:int, category_id:int, new_hist:schemas.ConsumeHistCreate, db:Session=Depends(get_db)):
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    category = crud.get_category(db, category_id=category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return crud.create_consume_hist(db,
                                        category_id=category_id,
                                        user_id=user_id,
                                        hist=new_hist,
                                        )

@app.put("/consume.history/{hist_id}", response_model=schemas.ConsumeHist)
def update_consume_history(hist_id: int, updated_hist: schemas.ConsumeHistCreate, user_id: int, category_id: int, db: Session = Depends(get_db)):
    return crud.update_consume_hist(db, hist_id=hist_id, updated_hist=updated_hist, user_id=user_id, category_id=category_id)

@app.delete("/consume.history/{hist_id}")
def delete_consume_history(hist_id: int, user_id: int, db: Session = Depends(get_db)):
    return crud.delete_consume_hist(db, hist_id=hist_id, user_id=user_id)

@app.get("/consume.history/{hist_id}", response_model=schemas.ConsumeHist)
def read_consume_history_by_id(hist_id: int, user_id: int, db: Session = Depends(get_db)):
    return crud.get_consume_hist_by_id(db, hist_id=hist_id, user_id=user_id)

@app.get("/budget/users/{user_id}", response_model=schemas.Budget)
def read_users_budget(user_id:int, db: Session = Depends(get_db)):
    user_by_id = crud.get_user(db, user_id=user_id)
    if user_by_id is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.get_budget(db, user_id=user_id)

@app.put("/budget/users/{user_id}/update", response_model=schemas.Budget)
def get_users_budget(user_id:int, budget: schemas.BudgetCreate, db: Session = Depends(get_db)):
    user_by_id = crud.get_user(db, user_id=user_id)
    if user_by_id is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_budget(db, user_id=user_id,updated_budget=budget)