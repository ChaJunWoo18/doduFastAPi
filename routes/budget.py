from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas, models, crud
from auth.login import get_current_active_user
from database import SessionLocal
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/get/budget", response_model=schemas.Budget)
def read_budget(current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    budget = crud.get_budget(db,user_id=current_user.id)
    if budget is None:
        raise HTTPException(status_code=404, detail="Budget is None")
    return budget

@router.put("/update/budget/byId", response_model=schemas.Budget)
def update_buget_by_user(amount:int, current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    budget = crud.get_budget(db,user_id=current_user.id)
    if budget is None:
        raise HTTPException(status_code=404, detail="Budget is None")
    budget.budget_amount = amount
    new_budget = crud.update_budget(db=db, user_id=current_user.id,updated_budget=budget)
    return new_budget

@router.put("/update/pre.budget/reset/month", response_model=schemas.Budget)
def update_pre_budget(current_user: models.User = Depends(get_current_active_user),db: Session = Depends(get_db)):
    updated_budget = crud.reset_monthly_budget(db, user_id=current_user.id)
    if not updated_budget:
        raise HTTPException(status_code=404, detail="Budget not found or error resetting budget")
    print("유저 pre_budget이 월 변경으로 자동 업데이트 되었습니다.")
    return updated_budget