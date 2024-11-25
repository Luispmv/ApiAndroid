from models import User, UserCreate, UserUpdate, UserBooks, Book, StatusEnum
from fastapi import APIRouter, HTTPException, status, Query
from db import SessionDep
from sqlmodel import select

router = APIRouter()

@router.post("/users", response_model=User, tags=["users"])
async def create_user(user_data: UserCreate, session: SessionDep):
    user = User.model_validate(user_data.model_dump())
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.get("/users", response_model=list[User], tags=["users"])
async def list_user(session: SessionDep):
    return session.exec(select(User)).all()

@router.get("/users/{user_id}", response_model=User, tags=["users"])
async def read_user(user_id: int, session: SessionDep):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail="User id doesn't exist")
    return user_db

@router.delete("/user/{user_id}", tags=["users"])
async def delete_user(user_id: int, session: SessionDep):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail="User id doesn't exist")
    session.delete(user_db)
    session.commit()
    return {"detail": "Deleted user"}

@router.patch("/user/{user_id}", response_model=User, status_code=status.HTTP_201_CREATED, tags=["users"])
async def update_user(user_id: int, user_data: UserUpdate,  session: SessionDep):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail="Customer id doesn't exist")
    custumer_data_dict = user_data.model_dump(exclude_unset=True)
    user_db.sqlmodel_update(custumer_data_dict)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db

@router.post("/users/{user_id}/books/{book_id}", tags=["users"])
async def subcribe_book_to_user(user_id: int, book_id: int,  session: SessionDep, book_status: StatusEnum = Query()):
    user_db = session.get(User, user_id)
    book_db = session.get(Book, book_id)

    if not user_db or not book_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The customer or plan doesn't exist"
        )
    user_book_db = UserBooks(
        book_id = book_db.id,
        user_id = user_db.id,
        status = book_status
    )

    session.add(user_book_db)
    session.commit()
    session.refresh(user_book_db)
    return user_book_db

@router.get("/users/{user_id}/books/", tags=["users"])
async def read_book_to_user(
        user_id: int,
        session: SessionDep,
        book_status: StatusEnum = Query()
):
    customer_db = session.get(User, user_id)
    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    query = (
        select(UserBooks)
        .where(UserBooks.customer_id == user_id)
        .where(UserBooks.status == book_status)
    )
    books = session.exec(query).all()
    return books