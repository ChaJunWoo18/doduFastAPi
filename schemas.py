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

class ConsumeHistResponse(ConsumeHistBase):
    id: int
    category_name: str

    class Config:
        from_attributes = True      


class TotalConsumeBase(BaseModel):
    month_total: int
    day_total: int

class TotalConsumeCreate(TotalConsumeBase):
    pass

class TotalConsume(TotalConsumeBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class BudgetBase(BaseModel):
    budget_amount: int
    pre_budget: int
    last_updated_date: date

class BudgetCreate(BudgetBase):
    pass


class Budget(BudgetBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: str
    nickname: str

class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    disabled: bool
    #total_consume: Optional[TotalConsume] = None

    class Config:
        from_attributes = True