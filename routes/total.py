from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud,schemas,models
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

@router.get("/get/total/consume", response_model=schemas.TotalConsume)
def read_total(current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    total_consume = crud.get_total_consume(db,user_id=current_user.id)
    if total_consume is None:
        raise HTTPException(status_code=404, detail="total_consume is None")
    return total_consume

@router.get("/get/total/consume/period")
def read_period_total(startDate:str, endDate:str,current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    period_total = crud.get_consume_hist_total(db=db,
                                                user_id=current_user.id,
                                                start_date=startDate,
                                                end_date=endDate)
    if period_total is None:
        raise HTTPException(status_code=404, detail="total_consume is None")
    return period_total

@router.put("/update/total/consume", response_model=schemas.TotalConsume)
def update_total_consume(month_total: int, day_total: int, current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    total = crud.get_total_consume(db,user_id=current_user.id)
    if total is None:
        raise HTTPException(status_code=404, detail="total_consume is None")
    total.month_total = month_total
    total.day_total = day_total
    updated_total = crud.update_total_consume(db=db, user_id=current_user.id,updated_total=total)
    return updated_total