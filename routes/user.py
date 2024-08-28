from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import crud,models
import schemas
from database import SessionLocal
from auth.login import get_current_user
from services import create_default_categories_for_user
from hash_pwd import hash_password,verify_password
from auth.login import get_current_active_user

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup", response_model=schemas.User)
def create_user(new_user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=new_user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    created_user = crud.create_user(db, user=new_user)
    create_default_categories_for_user(db, user_id=created_user.id)

    return created_user


@router.get("/check_use/nickname")
def check_nickname(nickname:str,db: Session = Depends(get_db)):
    db_user = crud.get_user_by_nickname(db=db, nickname=nickname)
    if db_user:
        raise HTTPException(status_code=400, detail="nickname already registered")
    return True

@router.get("/check_use/email")
def check_email(email:str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return True

@router.get("/get/me", response_model=schemas.User)
async def read_user(current_user: schemas.User = Depends(get_current_user)):
    return current_user


@router.get("/get/user/all")
def read_user_all(db: Session = Depends(get_db)):
    return crud.get_users(db)

#관리자 전용
@router.delete("/delete/user")
def remove_user(user_id:int, db:Session=Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=400, detail="User no exist")
    return crud.delete_user(db, db_user)

@router.put("/update/ban.state")
def ban_update(user_id:str, db:Session=Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=400, detail="User no exist")
    return crud.update_ban_state(db, db_user)

class ChangePassword(BaseModel):
    passwd: str
    new_passwd:str
#for user
@router.put("/update/password")
def password_update(request: ChangePassword, 
                    current_user: models.User = Depends(get_current_active_user),
                    db: Session = Depends(get_db)):
    passwd = request.passwd
    new_passwd = request.new_passwd
    db_user = crud.get_user(db, current_user.id)
    if db_user is None:
        raise HTTPException(status_code=400, detail="User not exist")
    # 현재 비밀번호가 일치하지 않을 경우
    if not verify_password(passwd, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    # 새 비밀번호를 해시화하여 저장
    db_user.hashed_password = hash_password(new_passwd)
    db.commit()
    db.refresh(db_user)
    return {"msg": "Password updated successfully"}

class PasswordRequest(BaseModel):
    passwd: str

@router.post("/confirm/password")
def confirm_pwd(request: PasswordRequest, 
                current_user: models.User = Depends(get_current_active_user),
                db: Session = Depends(get_db)):
    passwd = request.passwd
    db_user = crud.get_user(db, current_user.id)
    if db_user is None:
        raise HTTPException(status_code=400, detail="User not exist")
    # 현재 비밀번호가 일치하지 않을 경우
    if not verify_password(passwd, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    return {"msg": "Password correct"}

class ChangeNickname(BaseModel):
    new_nickname: str
  
#for user
@router.put("/update/nickname")
def nickname_update(request: ChangeNickname, 
                    current_user: models.User = Depends(get_current_active_user),
                    db: Session = Depends(get_db)):
    new_nickname = request.new_nickname

    db_user = crud.get_user_by_nickname(db=db, nickname=new_nickname)
    if db_user:
        raise HTTPException(status_code=400, detail="nickname already registered")

    db_user = crud.get_user(db, current_user.id)
    if db_user is None:
        raise HTTPException(status_code=400, detail="User not exist")
    # 현재 비밀번호가 일치하지 않을 경우
    crud.update_nickname(new_nickname, db, db_user)
    db.commit()
    db.refresh(db_user)
    return {"msg": "Nickname updated successfully"}