from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud
import models
import schemas
from database import SessionLocal, engine
from services import create_default_categories_for_user

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/signup", response_model=schemas.User)
def create_user(new_user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=new_user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    created_user = crud.create_user(db=db, user=new_user)
    #기본 카테고리 추가
    create_default_categories_for_user(db, user_id=created_user.id)
    return crud.create_user(db=db, user=new_user)


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
    return crud.update_consume_hist(db=db, hist_id=hist_id, updated_hist=updated_hist, user_id=user_id, category_id=category_id)

@app.delete("/consume.history/{hist_id}")
def delete_consume_history(hist_id: int, user_id: int, db: Session = Depends(get_db)):
    return crud.delete_consume_hist(db=db, hist_id=hist_id, user_id=user_id)

@app.get("/consume.history/{hist_id}", response_model=schemas.ConsumeHist)
def read_consume_history_by_id(hist_id: int, user_id: int, db: Session = Depends(get_db)):
    return crud.get_consume_hist_by_id(db=db, hist_id=hist_id, user_id=user_id)
