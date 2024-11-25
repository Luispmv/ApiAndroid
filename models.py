from pydantic import BaseModel, EmailStr, field_validator
from sqlmodel import SQLModel, Field, Relationship, Session, select
from enum import Enum
from db import engine

class StatusEnum(str, Enum):
    ACTIVE = "favorite"
    INACTIVE = ""

class CustomerPlan(SQLModel, table=True):
    id: int = Field(primary_key=True)
    plan_id: int = Field(foreign_key="plan.id")
    customer_id: int = Field(foreign_key="customer.id")
    status: StatusEnum = Field(default=StatusEnum.ACTIVE)

class  BookBase(SQLModel):
    title: str = Field(default=None)
    author: str = Field(default=None)
    year: str = Field(default=None)
    category: str = Field(default=None)
    num_pages: int = Field(default=None)
    image: str = Field(default=None)

class

class Book(BookBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    users: list["User"] = Relationship(
        back_populates="plans", link_model=CustomerPlan
    )

class UserBase(SQLModel):
    name: str = Field(default=None)
    email: EmailStr = Field(default=None)
    password: str | None = Field(default=None)


    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        session = Session(engine)
        query = select(Customer).where(Customer.email == value)
        result = session.exec(query).first()
        if result:
            raise ValueError("This email is alredy registered")
        return value

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    books: list[Book] = Relationship(
        back_populates="customers", link_model=CustomerPlan
    )