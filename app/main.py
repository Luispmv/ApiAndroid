from fastapi import FastAPI
from db import create_all_tables
from .routers import user, book

app = FastAPI(lifespan=create_all_tables)
app.include_router(user.router)
app.include_router(book.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}