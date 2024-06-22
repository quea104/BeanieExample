from fastapi import FastAPI
import asyncio

from database import init

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    await init()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
