from sqlalchemy.orm import Session
from hash_pwd import hash_password, verify_password
import models
import schemas
from fastapi import HTTPException
import datetime
from redisConfig import rd
import json
from sqlalchemy import select, func
from typing import List, Dict
from datetime import date

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_nickname(db: Session, nickname: str):

    return db.query(models.User).filter(models.User.nickname == nickname).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def delete_user(db:Session, db_user: models.User):
    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted"}

def update_ban_state(db:Session, db_user: models.User):
    db_user.disabled = not db_user.disabled
    db.commit()
    return {"detail": "Ban state updated"}

def update_nickname(new_nickname:str, db: Session, db_user:models.User):
    db_user.nickname = new_nickname
    db.commit()
    return {"detail": "Nickname updated"}

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = hash_password(user.password)
    new_budget = models.Budget(budget_amount=0, pre_budget=0)
    new_total_consume = models.TotalConsume(month_total=0, day_total=0)
    db_user = models.User(email=user.email, 
                          hashed_password=hashed_password,
                          nickname = user.nickname,
                          budget=new_budget,
                          total_consume = new_total_consume)
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

def delete_category(db:Session, category_name: str, user_id:int):
    category = db.query(models.Category).filter(models.Category.owner_id == user_id)\
        .filter(models.Category.name==category_name).first()
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

# ###consumeHist###
# def get_consume_history_old(db: Session, user_id: int):
#     return db.query(models.ConsumeHist, models.Category.name.label('name'))\
#         .join(models.Category)\
#         .filter(models.ConsumeHist.user_id == user_id)\
#         .all()

# 날짜 객체를 문자열로 변환하는 함수
def date_converter(o):
    if isinstance(o, date):
        return o.strftime("%Y-%m-%d")
    raise TypeError(f"Type {o} not serializable")

def get_consume_history(db: Session, user_id: int, start_date:str,end_date:str)-> List[Dict]:
    cache_key = f"user:{user_id}:consume_hist:{start_date}:{end_date}"
    cached_data = rd.get(cache_key)

    if cached_data:
        print("it's cached_data")
        return json.loads(cached_data)
    stmt = select(
        models.ConsumeHist.id,
        models.ConsumeHist.receiver,
        models.ConsumeHist.date,
        models.ConsumeHist.amount,
        models.Category.name.label('name')
    )\
    .filter(
        models.ConsumeHist.user_id == user_id,
        models.ConsumeHist.date >= start_date,
        models.ConsumeHist.date <= end_date   
    )
    # .join(
    #     models.Category, models.ConsumeHist.category_id == models.Category.id
    # )
    result = db.execute(stmt).fetchall()
    if(len(result)>0):
        result_dict = [dict(row._mapping) for row in result]
        rd.set(cache_key, json.dumps(result_dict, default=date_converter), ex=60*5) 
        return result_dict
    #print(f"No data found for user_id: {user_id}, start_date: {start_date}, end_date: {end_date}")
    raise HTTPException(status_code=400, detail="History not found")

#기간 소비
def get_consume_hist_total(db: Session, user_id: int, start_date:str,end_date:str)-> int:
    cache_key = f"user:{user_id}:consume_hist_total:{start_date}:{end_date}"
    cached_data = rd.get(cache_key)
    print(cached_data)
    if cached_data:
        return float(cached_data)
    
    stmt = select(
        func.sum(models.ConsumeHist.amount).label('total_amount')
    ).filter(
        models.ConsumeHist.user_id == user_id,
        models.ConsumeHist.date >= start_date, 
        models.ConsumeHist.date <= end_date   
    )
    
    result = db.execute(stmt).scalar_one_or_none()
    total_amount = result if result is not None else 0
    rd.set(cache_key, total_amount, ex=60*5)
    return total_amount

#데이터 추가
def create_consume_hist(db:Session,hist:schemas.ConsumeHistCreate, user_id:int, category_id:str):
    db_hist = models.ConsumeHist(receiver = hist.receiver,
                                 date = hist.date,
                                 amount = hist.amount,
                                 user_id = user_id,
                                 category_id = category_id)
    db.add(db_hist)
    db.commit()
    db.refresh(db_hist)
    return db_hist

# def update_consume_hist(db: Session, hist_id: int, updated_hist: schemas.ConsumeHistCreate, user_id: int, category_id: int):
#     # 소비 기록 찾기
#     db_hist = get_consume_hist_by_id(hist_id=hist_id, user_id=user_id)
#     if db_hist is None:
#         raise HTTPException(status_code=404, detail="Consume history not found")

#     # 기록 업데이트
#     db_hist.receiver = updated_hist.receiver
#     db_hist.date = updated_hist.date
#     db_hist.amount = updated_hist.amount
#     db_hist.category_id = category_id  # 카테고리 ID도 업데이트
    
#     db.commit()
#     db.refresh(db_hist)
#     return db_hist
#데이터 삭제
def delete_consume_hist(db: Session, hist_id: int, user_id: int):
    # 특정 패턴에 맞는 모든 키 가져오기
    pattern = f"user:{user_id}:consume_hist:*"
    keys = rd.scan_iter(pattern)

    # 매칭된 모든 키 삭제
    for key in keys:
        rd.delete(key)

    db_hist = get_consume_hist_by_id(db=db,hist_id=hist_id, user_id=user_id)
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

def create_total(db: Session, total_consume: schemas.TotalConsumeCreate, user_id: int):
    db_total = total_consume(month_total = 0, day_total=0, user_id=user_id)
    db.add(db_total)
    db.commit()
    db.refresh(db_total)
    return db_total

def reset_monthly_budget(db: Session, user_id: int):
    budget = db.query(models.Budget).filter(models.Budget.user_id == user_id).first()
    if not budget:
        return None

    today = datetime.datetime.now().date()
    #db_
    db_last_date = str(budget.last_updated_date).split('-')
    db_last_date_year = int(db_last_date[0])
    db_last_date_month = int(db_last_date[1])
    #print(pre_budget_year==today.year, int(pre_budget_month)==today.month)
    if today.month != db_last_date_month or today.year != db_last_date_year:
        budget.pre_budget = budget.budget_amount
        budget.last_updated_date = today

        db.commit()
        db.refresh(budget)

    return budget

def get_total_consume(db: Session, user_id: int):
    db_total = db.query(models.TotalConsume).filter(models.TotalConsume.user_id == user_id).first()
    if db_total is None:
        raise HTTPException(status_code=404, detail="consumeTotal not found")
    return db_total

def update_total_consume(db: Session, user_id: int, updated_total: schemas.TotalConsume):
    db_total = get_total_consume(db, user_id= user_id)
    if db_total is None:
        raise HTTPException(status_code=404, detail="consumeTotal not found")
    
    db_total.day_total = updated_total.day_total
    db_total.month_total = updated_total.month_total
    db.commit()
    db.refresh(db_total)
    return db_total