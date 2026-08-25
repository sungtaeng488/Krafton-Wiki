import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

_mongo_client = None


def get_mongo_client():
    global _mongo_client

    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise RuntimeError("MONGO_URI 환경변수가 설정되지 않았습니다.")

    if _mongo_client is None:
        _mongo_client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=10_000,
            tz_aware=True,
        )

    return _mongo_client


def get_database():
    database_name = os.getenv("MONGO_DB_NAME", "krafton_wiki")
    return get_mongo_client()[database_name]


def close_mongo_client():
    global _mongo_client

    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
