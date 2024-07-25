from sqlalchemy.orm import Session
import models

def create_default_categories_for_user(db: Session, user_id: int):
    # 기본 카테고리 목록
    default_categories = [
        {"name": "음식"},
        {"name": "카페"},
        {"name": "운동"},
        {"name": "병원"},
        {"name": "쇼핑"}
    ]
    
    for category in default_categories:
        # 이미 카테고리가 존재하는지 확인
        existing_category = db.query(models.Category).filter(
            models.Category.name == category["name"],
            models.Category.owner_id == user_id
        ).first()
        if existing_category is None:
            # 카테고리 추가
            db_category = models.Category(name=category["name"], owner_id=user_id)
            db.add(db_category)
    
    db.commit()