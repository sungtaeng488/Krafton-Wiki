from datetime import datetime, timezone

from pymongo import ASCENDING, DESCENDING

from db.collections import get_post_histories_collection, get_posts_collection


HISTORY_CONTENT_FIELDS = ("title", "summary", "content", "tags")
_history_indexes_ready = False


def ensure_post_history_indexes():
    global _history_indexes_ready
    if _history_indexes_ready:
        return

    histories = get_post_histories_collection()
    histories.create_index(
        [("post_id", ASCENDING), ("version", ASCENDING)],
        unique=True,
        name="unique_post_version",
    )
    histories.create_index(
        [("post_id", ASCENDING), ("version", DESCENDING)],
        name="post_history_latest_first",
    )
    _history_indexes_ready = True


def make_history_document(post_id, version, post_data, edited_by, created_at=None):
    return {
        "post_id": post_id,
        "version": version,
        **{
            field: post_data.get(field, [] if field == "tags" else "")
            for field in HISTORY_CONTENT_FIELDS
        },
        "edited_by": edited_by,
        "created_at": created_at or datetime.now(timezone.utc),
    }


def save_post_history(post_id, version, post_data, edited_by, created_at=None):
    ensure_post_history_indexes()
    document = make_history_document(
        post_id,
        version,
        post_data,
        edited_by,
        created_at,
    )
    get_post_histories_collection().update_one(
        {"post_id": post_id, "version": version},
        {"$setOnInsert": document},
        upsert=True,
    )
    return document


def ensure_initial_post_history(post, posts=None):
    if posts is None:
        posts = get_posts_collection()
    version = post.get("version")

    if not isinstance(version, int) or version < 1:
        version = 1
        posts.update_one(
            {"_id": post["_id"]},
            {"$set": {"version": version}},
        )
        post["version"] = version

    edited_by = post.get("user_id") or post.get("author") or "알 수 없음"
    snapshot_time = post.get("updated_at") or post.get("created_at")
    save_post_history(
        post["_id"],
        version,
        post,
        edited_by,
        snapshot_time,
    )
    return version


def list_post_histories(post_id):
    ensure_post_history_indexes()
    return list(
        get_post_histories_collection()
        .find({"post_id": post_id})
        .sort("version", DESCENDING)
    )


def get_post_history(post_id, version):
    ensure_post_history_indexes()
    return get_post_histories_collection().find_one(
        {"post_id": post_id, "version": version}
    )
