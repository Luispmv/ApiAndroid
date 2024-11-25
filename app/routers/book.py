from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from models import Book, BookCreate, BookUpdate
from db import SessionDep

router = APIRouter()


@router.post("/books", response_model=Book, tags=["books"])
async def create_book(book_data: BookCreate, session: SessionDep):
    book = Book.model_validate(book_data.model_dump())
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


@router.get(
    "/books",
    response_model=list[Book],
    tags=["books"]
)
async def list_book(session: SessionDep):
    return session.exec(select(Book)).all()


@router.get(
    "/books/{book_id}",
    response_model=Book,
    tags=["books"]
)
async def read_book(book_id: int, session: SessionDep):
    book_db = session.get(Book, book_id)
    if not book_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="book doesn't exist"
        )
    return book_db


@router.get(
    "/books/{book_category}",
    response_model=Book,
    tags=["books"]
)
async def read_book_by_category(book_category: str, session: SessionDep):
    book_db = session.get(Book, book_category)
    if not book_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="category doesn't exist"
        )
    return book_db


@router.delete(
    "/books/{book_id}",
    tags=["books"]
)
async def delete_user(book_id: int, session: SessionDep):
    book_db = session.get(Book, book_id)
    if not book_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="book doesn't exist"
        )
    session.delete(book_db)
    session.commit()
    return {"detail": "Deleted book"}


@router.patch("/books/{book_id}", response_model=Book, status_code=status.HTTP_201_CREATED, tags=["books"])
async def update_book(book_id: int, book_data: BookUpdate, session: SessionDep):
    book_db = session.get(Book, book_id)
    if not book_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer doesn't exist"
        )
    book_data_dict = book_data.model_dump(exclude_unset=True)
    book_db.sqlmodel_update(book_data_dict)
    session.add(book_db)
    session.commit()
    session.refresh(book_db)
    return book_db
