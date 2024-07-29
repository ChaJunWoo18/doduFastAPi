from sqlalchemy.orm import Session
from hash_pwd import hash_password, verify_password
import models
import schemas
from fastapi import HTTPException

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = hash_password(user.password)
    db_user = models.User(email=user.email, 
                          hashed_password=hashed_password,
                          username = user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str): #로그인
    user = get_user_by_email(db, email)
    if user and verify_password(password, user.hashed_password):
        return user
    return None

def create_category(db:Session, category:schemas.CategoryCreate, user_id: int):
    db_category = models.Category(name = category.name, owner_id = user_id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db:Session, category_id: int, user_id:int):
    category = db.query(models.Category).filter(models.Category.owner_id == user_id)\
        .filter(models.Category.id==category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return {"detail": "Category deleted"}

def get_category_by_name(db:Session, category_name: str):
    return db.query(models.Category).filter(models.Category.name == category_name).first()

def get_category(db:Session, category_id: int):
    return db.query(models.Category).filter(models.Category.id == category_id).first()

def get_categories_by_id(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.Category).filter(models.Category.owner_id == user_id).offset(skip).limit(limit).all()

###consumeHist###
def get_consume_history_by_user_id(db: Session, user_id: int):
    return db.query(models.ConsumeHist).filter(models.ConsumeHist.user_id == user_id).all()

def create_consume_hist(db:Session,hist:schemas.ConsumeHistCreate, user_id:int, category_id:int):
    db_hist = models.ConsumeHist(receiver = hist.receiver,
                                 date = hist.date,
                                 amount = hist.amount,
                                 user_id = user_id,
                                 category_id = category_id)
    db.add(db_hist)
    db.commit()
    db.refresh(db_hist)
    return db_hist

def update_consume_hist(db: Session, hist_id: int, updated_hist: schemas.ConsumeHistCreate, user_id: int, category_id: int):
    # 소비 기록 찾기
    db_hist = get_consume_hist_by_id(hist_id=hist_id, user_id=user_id)
    if db_hist is None:
        raise HTTPException(status_code=404, detail="Consume history not found")

    # 기록 업데이트
    db_hist.receiver = updated_hist.receiver
    db_hist.date = updated_hist.date
    db_hist.amount = updated_hist.amount
    db_hist.category_id = category_id  # 카테고리 ID도 업데이트
    
    db.commit()
    db.refresh(db_hist)
    return db_hist

def delete_consume_hist(db: Session, hist_id: int, user_id: int):
    db_hist = get_consume_hist_by_id(hist_id=hist_id, user_id=user_id)
    if db_hist is None:
        raise HTTPException(status_code=404, detail="Consume history not found")
    db.delete(db_hist)
    db.commit()
    return {"detail": "Consume history deleted"}

def get_consume_hist_by_id(db: Session, hist_id: int, user_id: int):
    db_hist = db.query(models.ConsumeHist).filter(models.ConsumeHist.id == hist_id, models.ConsumeHist.user_id == user_id).first()
    if db_hist is None:
        raise HTTPException(status_code=404, detail="Consume history not found")
    return db_hist

def get_budget(db: Session, user_id: int):
    db_budget = db.query(models.Budget).filter(models.Budget.user_id == user_id).first()
    if db_budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    return db_budget

def update_budget(db: Session, user_id: int, updated_budget: schemas.Budget):
    db_budget = get_budget(db, user_id= user_id)
    if db_budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    db_budget.budget_amount = updated_budget.budget_amount
    db_budget.pre_budget = updated_budget.pre_budget
    db.commit()
    db.refresh(db_budget)
    return db_budget

def create_budget(db:Session, user_id: int):
    db_budget= models.Budget(budget_amount = 0,
                             pre_budget= 0,
                             user_id= user_id)
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

def decode_token(db:Session,token):
    user = get_user_by_email(db,token)
    return user