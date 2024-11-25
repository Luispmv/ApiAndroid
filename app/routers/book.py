from fastapi import APIRouter, HTTPException, status, Query
from sqlmodel import select
from models import Book, BookCreate, BookUpdate
from db import SessionDep

router = APIRouter()

# 1. Recuperar todos los libros con paginación
@router.get("/books/list", tags=["books"])
async def list_books(
    session: SessionDep,
    skip: int = Query(0, description="Registros a omitir"),
    limit: int = Query(10, description="Número de registros")
):
    query = select(Book).offset(skip).limit(limit)
    books = session.exec(query).all()
    return books

# 2. Recuperar un libro por ID
@router.get("/books/id/{book_id}", response_model=Book, tags=["books"])
async def read_book(book_id: int, session: SessionDep):
    book_db = session.get(Book, book_id)
    if not book_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="book doesn't exist"
        )
    return book_db

# 3. Recuperar libros por categoría
@router.get("/books/{book_category}", response_model=list[Book], tags=["books"])
async def read_books_by_category(book_category: str, session: SessionDep):
    query = select(Book).where(Book.category == book_category)
    books = session.exec(query).all()

    if not books:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No books found in category '{book_category}'"
        )

    return books

# 4. Recuperar todos los libros (sin paginación)
@router.get("/books", response_model=list[Book], tags=["books"])
async def list_book_complete(session: SessionDep):
    return session.exec(select(Book)).all()

# 5. Crear un nuevo libro
@router.post("/books", response_model=Book, tags=["books"])
async def create_book(book_data: BookCreate, session: SessionDep):
    book = Book.model_validate(book_data.model_dump())
    session.add(book)
    session.commit()
    session.refresh(book)
    return book

# 6. Actualizar un libro por ID
@router.patch("/books/{book_id}", response_model=Book, status_code=status.HTTP_200_OK, tags=["books"])
async def update_book(book_id: int, book_data: BookUpdate, session: SessionDep):
    book_db = session.get(Book, book_id)
    if not book_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book doesn't exist"
        )
    book_data_dict = book_data.model_dump(exclude_unset=True)
    book_db.sqlmodel_update(book_data_dict)
    session.add(book_db)
    session.commit()
    session.refresh(book_db)
    return book_db

# 7. Eliminar un libro por ID
@router.delete("/books/{book_id}", tags=["books"])
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
