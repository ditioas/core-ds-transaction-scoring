from typing import Any

from loguru import logger
from pymongo import MongoClient

from app.config import settings


class MongoDBConnectionError(Exception):
    """Raised when unable to connect to MongoDB."""


def get_client() -> MongoClient[dict[str, Any]]:
    try:
        client: MongoClient[dict[str, Any]] = MongoClient(settings.MONGO_URI)
        logger.info("Connection to Mongo DB is established.")
        return client
    except Exception as e:
        logger.error(f"Mongo DB connection error occurred: {e}")
        raise MongoDBConnectionError("Could not connect to MongoDB.")
