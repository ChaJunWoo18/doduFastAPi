from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud
import schemas,models
from auth.login import get_current_active_user
from database import SessionLocal
import redisConfig
router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas.ConsumeHistResponse])
async def read_consume_history(current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id=current_user.id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    consume_hist_list = await crud.get_consume_history(db, user_id=current_user.id,limit=100, offset=0)
    if not consume_hist_list:
        raise HTTPException(status_code=404, detail="History not found")

    return [
        schemas.ConsumeHistResponse(
            id=row["id"],
            receiver=row["receiver"],
            date=row["date"],
            amount=row["amount"],
            category_name=row["name"]
        )
        for row in consume_hist_list
    ]

@router.post("/add/new_history")
def create_consume_history(category_name:str, new_hist: schemas.ConsumeHistCreate,current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id=current_user.id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    category = crud.get_category_by_name(db, category_name=category_name)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return crud.create_consume_hist(db, category_id=category.id, user_id=user.id, hist=new_hist)

@router.put("/{hist_id}", response_model=schemas.ConsumeHist)
def update_consume_history(hist_id: int, updated_hist: schemas.ConsumeHistCreate, user_id: int, category_id: int, db: Session = Depends(get_db)):
    return crud.update_consume_hist(db, hist_id=hist_id, updated_hist=updated_hist, user_id=user_id, category_id=category_id)

@router.delete("/{hist_id}")
def delete_consume_history(hist_id: int, user_id: int, db: Session = Depends(get_db)):
    return crud.delete_consume_hist(db, hist_id=hist_id, user_id=user_id)

@router.get("/{hist_id}", response_model=schemas.ConsumeHist)
def read_consume_history_by_id(hist_id: int, user_id: int, db: Session = Depends(get_db)):
    return crud.get_consume_hist_by_id(db, hist_id=hist_id, user_id=user_id)
