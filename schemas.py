from pydantic import BaseModel
from datetime import date

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class ConsumeHistBase(BaseModel):
    receiver: str
    date: date
    amount: int

class ConsumeHistCreate(ConsumeHistBase):
    pass

class ConsumeHist(ConsumeHistBase):
    id: int
    user_id: int
    category_id: int

    class Config:
        from_attributes = True 


class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    disabled: bool 
    #consume_histories: list[ConsumeHist] = []

    class Config:
        from_attributes = True


class BudgetBase(BaseModel):
    budget_amount: int
    pre_budget: int


class BudgetCreate(BudgetBase):
    pass


class Budget(BudgetBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True