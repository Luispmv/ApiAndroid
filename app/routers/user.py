from models import User, UserCreate, UserUpdate, UserBooks, Book, StatusEnum
from fastapi import APIRouter, HTTPException, status, Query
from db import SessionDep
from sqlmodel import select
from passlib.context import CryptContext

router = APIRouter()

# 1. Listar todos los usuarios
@router.get("/users", response_model=list[User], tags=["users"])
async def list_user(session: SessionDep):
    return session.exec(select(User)).all()

# 2. Consultar un usuario por ID
@router.get("/users/{user_id}", response_model=User, tags=["users"])
async def read_user(user_id: int, session: SessionDep):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User doesn't exist"
        )
    return user_db

# 3. Consultar libros asociados a un usuario por estado
@router.get("/users/{user_id}/books/", tags=["users"])
async def read_book_to_user(
    user_id: int,
    session: SessionDep,
    book_status: StatusEnum = Query()
):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User doesn't exist"
        )

    query = (
        select(UserBooks)
        .where(UserBooks.user_id == user_id)
        .where(UserBooks.status == book_status)
    )
    books = session.exec(query).all()
    return books

# 4. Crear un nuevo usuario
@router.post("/users", response_model=User, tags=["users"])
async def create_user(user_data: UserCreate, session: SessionDep):
    # Hash de la contraseña
    hashed_password = pwd_context.hash(user_data.password)
    user_data.password = hashed_password
    # Crear usuario
    user = User.model_validate(user_data.model_dump())
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# 5. Asociar un libro a un usuario
@router.post("/users/{user_id}/books/{book_id}", tags=["users"])
async def subscribe_book_to_user(
    user_id: int,
    book_id: int,
    session: SessionDep,
    book_status: StatusEnum = Query()
):
    user_db = session.get(User, user_id)
    book_db = session.get(Book, book_id)

    if not user_db or not book_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user or book doesn't exist"
        )
    user_book_db = UserBooks(
        book_id=book_db.id,
        user_id=user_db.id,
        status=book_status
    )

    session.add(user_book_db)
    session.commit()
    session.refresh(user_book_db)
    return user_book_db

# 6. Actualizar un usuario por ID
@router.patch("/users/{user_id}", response_model=User, status_code=status.HTTP_200_OK, tags=["users"])
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: SessionDep
):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User doesn't exist"
        )

    user_data_dict = user_data.model_dump(exclude_unset=True)

    if "password" in user_data_dict:
        user_data_dict["password"] = pwd_context.hash(user_data_dict["password"])

    user_db.sqlmodel_update(user_data_dict)

    session.add(user_db)
    session.commit()
    session.refresh(user_db)

    return user_db

# 7. Eliminar un usuario
@router.delete("/users/{user_id}", tags=["users"])
async def delete_user(user_id: int, session: SessionDep):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User doesn't exist"
        )
    session.delete(user_db)
    session.commit()
    return {"detail": "Deleted user"}



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/login", tags=["auth"], summary="User login")
async def login(email: str, password: str, session: SessionDep):
    # Buscar al usuario por correo electrónico
    query = select(User).where(User.email == email)
    user_db = session.exec(query).first()

    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    # Verificar la contraseña
    if not pwd_context.verify(password, user_db.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )
    # Devolver los atributos del usuario con su ID
    return user_db
