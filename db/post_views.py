from datetime import datetime, timedelta, timezone

from pymongo import ASCENDING

from db.collections import get_post_view_events_collection


VIEW_EVENT_TTL_SECONDS = 60 * 60 * 24
_view_indexes_ready = False


def ensure_post_view_indexes():
    global _view_indexes_ready
    if _view_indexes_ready:
        return

    events = get_post_view_events_collection()
    events.create_index(
        [("post_id", ASCENDING), ("viewed_at", ASCENDING)],
        name="post_views_by_time",
    )
    events.create_index(
        "viewed_at",
        expireAfterSeconds=VIEW_EVENT_TTL_SECONDS,
        name="expire_post_views_after_24h",
    )
    _view_indexes_ready = True


def record_post_view(post_id, viewer_key, viewed_at=None):
    ensure_post_view_indexes()
    event = {
        "post_id": post_id,
        "viewer_key": viewer_key,
        "viewed_at": viewed_at or datetime.now(timezone.utc),
    }
    get_post_view_events_collection().insert_one(event)
    return event


def get_views_24h_by_post(post_ids, now=None):
    if not post_ids:
        return {}

    ensure_post_view_indexes()
    cutoff = (now or datetime.now(timezone.utc)) - timedelta(hours=24)
    pipeline = [
        {
            "$match": {
                "post_id": {"$in": list(post_ids)},
                "viewed_at": {"$gte": cutoff},
            }
        },
        {"$group": {"_id": "$post_id", "count": {"$sum": 1}}},
    ]
    return {
        result["_id"]: result["count"]
        for result in get_post_view_events_collection().aggregate(pipeline)
    }
