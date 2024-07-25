from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship

from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    username = Column(String)
    #is_active = Column(Boolean, default=True)

    items = relationship("Category", back_populates="owner")
    consume_histories = relationship("ConsumeHist", back_populates="user")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)

    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")
    consume_histories = relationship("ConsumeHist", back_populates="category")

class ConsumeHist(Base):
    __tablename__ = "consume_hist"

    id = Column(Integer, primary_key=True)
    receiver = Column(String)
    date = Column(Date, index=True)
    amount = Column(Integer)

    user_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))

    user = relationship("User", back_populates="consume_histories")
    category = relationship("Category", back_populates="consume_histories")
