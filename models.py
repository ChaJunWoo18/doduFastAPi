from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship
import datetime
from database import Base
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    nickname = Column(String)
    disabled = Column(Boolean, default=False)

    items = relationship("Category", back_populates="owner", cascade="all, delete-orphan")
    consume_histories = relationship("ConsumeHist", back_populates="user", cascade="all, delete-orphan")
    budget = relationship("Budget", uselist=False, back_populates="user", cascade="all, delete-orphan")
    total_consume = relationship("TotalConsume", uselist=False, back_populates="user", cascade="all, delete-orphan")

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

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    budget_amount = Column(Integer, default=0)
    pre_budget = Column(Integer, default=0)
    last_updated_date = Column(Date, default=datetime.datetime.now().date()) #datetime.datetime.now().date()) #pre_budeget update시에만 업데이트할 것

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="budget")

class TotalConsume(Base):
    __tablename__ = "total_consumes"

    id = Column(Integer, primary_key=True, index=True)
    month_total = Column(Integer, default=0)
    day_total = Column(Integer, default=0)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="total_consume")