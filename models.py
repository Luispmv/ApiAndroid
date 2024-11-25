from pydantic import BaseModel, EmailStr, field_validator
from sqlmodel import SQLModel, Field, Relationship, Session, select
from enum import Enum
from db import engine

class StatusEnum(str, Enum):
    ACTIVE = "favorite"
    INACTIVE = ""

class UserBooks(SQLModel, table=True):
    id: int = Field(primary_key=True)
    book_id: int = Field(foreign_key="book.id")
    user_id: int = Field(foreign_key="user.id")
    status: StatusEnum = Field(default=StatusEnum.ACTIVE)

class BookBase(SQLModel):
    title: str = Field(default=None)
    author: str = Field(default=None)
    year: str = Field(default=None)
    category: str = Field(default=None)
    num_pages: int = Field(default=None)
    image: str = Field(default=None)

class BookCreate(BookBase):
    pass

class BookUpdate(BookBase):
    pass


class Book(BookBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    users: list["User"] = Relationship(
        back_populates="books", link_model=UserBooks
    )

class UserBase(SQLModel):
    name: str = Field(default=None)
    email: EmailStr = Field(default=None)
    password: str | None = Field(default=None)


    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        session = Session(engine)
        query = select(User).where(User.email == value)
        result = session.exec(query).first()
        if result:
            raise ValueError("This email is alredy registered")
        return value

class UserCreate(BookBase):
    pass

class UserUpdate(BookBase):
    pass

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    books: list[Book] = Relationship(
        back_populates="users", link_model=UserBooks
    )