from datetime import timedelta, timezone

from pymongo import DESCENDING, UpdateOne

from data.mock_posts import MOCK_POSTS
from db import close_mongo_client, get_database


SEOUL_TIMEZONE = timezone(timedelta(hours=9))


def as_utc(value):
    if value.tzinfo is None:
        value = value.replace(tzinfo=SEOUL_TIMEZONE)

    return value.astimezone(timezone.utc)


def make_post_document(post):
    document = {**post}
    document.pop("id", None)
    document["created_at"] = as_utc(document["created_at"])
    document["updated_at"] = document["created_at"]
    document["status"] = "published"
    return document


def create_post_indexes(posts):
    posts.create_index("slug", unique=True, name="unique_post_slug")
    posts.create_index(
        [("created_at", DESCENDING)],
        name="posts_by_created_at",
    )
    posts.create_index(
        [("views", DESCENDING)],
        name="posts_by_views",
    )
    posts.create_index(
        [("likes", DESCENDING)],
        name="posts_by_likes",
    )


def seed_posts():
    database = get_database()
    posts = database["posts"]
    create_post_indexes(posts)

    documents = [make_post_document(post) for post in MOCK_POSTS]
    operations = [
        UpdateOne(
            {"slug": document["slug"]},
            {"$set": document},
            upsert=True,
        )
        for document in documents
    ]
    result = posts.bulk_write(operations)
    seeded_count = posts.count_documents(
        {"slug": {"$in": [document["slug"] for document in documents]}}
    )

    print(f"database={database.name}")
    print(f"collection={posts.name}")
    print(f"matched={result.matched_count}")
    print(f"modified={result.modified_count}")
    print(f"upserted={result.upserted_count}")
    print(f"seeded_posts={seeded_count}")


if __name__ == "__main__":
    try:
        seed_posts()
    finally:
        close_mongo_client()
