from app.config import get_settings

from typing import Generator

from pymongo import MongoClient
from fastapi import FastAPI

settings = get_settings()


_client: MongoClient | None = None
_db = None

def connect_to_mongo(app: FastAPI | None = None) -> None:
    global _client, _db
    if _client is None:
        _client = MongoClient(f'mongodb+srv://{settings.MONGO_DB_ADMIN}:{settings.MONGO_DB_ADM_PW}@{settings.MONGO_DB_CL}')
        _db = _client[settings.MONGO_API_DB]

        _client.admin.command("ping")

    if app:
        app.state.mongo_client = _client
        app.state.mongo_db = _db

def close_mongo() -> None:
    global _client, _db
    if _client:
        _client.close()
    _client = None
    _db = None

def get_db() -> Generator:
    if _db is None:
        raise RuntimeError("MongoDB not initialized; call connect_to_mongo on startup")
    yield _db