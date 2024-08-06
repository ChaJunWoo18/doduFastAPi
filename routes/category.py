from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import crud
import schemas, models
from auth.login import get_current_active_user
from database import SessionLocal

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/add", response_model=schemas.Category)
def create_category_for_user(new_category: schemas.CategoryCreate, current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    existing_category = crud.get_category_by_name(db, category_name=new_category.name)
    if existing_category:
        raise HTTPException(status_code=400, detail="Category already exist")
    return crud.create_category(db, category=new_category, user_id=current_user.id)

# @router.get("/categories/", response_model=List[schemas.Category])
# def read_categories(current_user: models.User = Depends(get_current_active_user), skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#     categories = crud.get_categories_by_id(db=db, skip=skip, limit=limit, user_id=current_user.id)
#     return categories

@router.get("/categories/", response_model=List[str])
def read_categories(current_user: models.User = Depends(get_current_active_user), skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    categories = crud.get_categories_by_id(db=db, skip=skip, limit=limit, user_id=current_user.id)
    cateList =  []
    for cateModel in categories:
        cateList.append(cateModel.name)
    return cateList

@router.delete("/del/one/{name}")
def remove_category(name: str,current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    print(name)
    return crud.delete_category(db=db, category_name=name, user_id=current_user.id)
