from db.mongo import get_database


def get_posts_collection():
    return get_database()["posts"]


def get_users_collection():
    return get_database()["users"]


def ensure_database_indexes():
    get_users_collection().create_index(
        "user_id",
        unique=True,
        name="unique_user_id",
    )
