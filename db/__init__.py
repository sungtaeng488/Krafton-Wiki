from db.collections import (
    ensure_database_indexes,
    get_post_histories_collection,
    get_post_view_events_collection,
    get_posts_collection,
    get_users_collection,
)
from db.mongo import close_mongo_client, get_database, get_mongo_client

# DB 내부 구현에 있는 다른 변수나 함수는 숨기고, 이 목록만 가져다 쓰게 함
__all__ = (
    "close_mongo_client",
    "ensure_database_indexes",
    "get_database",
    "get_mongo_client",
    "get_post_histories_collection",
    "get_post_view_events_collection",
    "get_posts_collection",
    "get_users_collection",
)
