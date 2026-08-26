from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from flask import Blueprint, render_template, url_for

from db import get_database


main_bp = Blueprint("main", __name__)
SEOUL_TIMEZONE = ZoneInfo("Asia/Seoul")

SORT_KEYS = {
    "trending": lambda post: post.get("views_24h", 0) + post.get("likes", 0) * 3,
    "views": lambda post: post.get("views", 0),
    "likes": lambda post: post.get("likes", 0),
    "latest": lambda post: post["created_at"],
}

PERIOD_LABELS = {
    "today": "오늘",
    "week": "이번 주",
    "month": "이번 달",
    "year": "올해",
}


def as_seoul_datetime(value):
    if value.tzinfo is None:
        return value.replace(tzinfo=SEOUL_TIMEZONE)

    return value.astimezone(SEOUL_TIMEZONE)


def normalize_created_at(post):
    created_at = post.get("created_at") or post.get("updated_at")

    if isinstance(created_at, str):
        created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M")

    if created_at is None:
        created_at = datetime.min.replace(tzinfo=SEOUL_TIMEZONE)

    return as_seoul_datetime(created_at)


def get_relative_time(created_at):
    created_at = as_seoul_datetime(created_at)
    now = datetime.now(SEOUL_TIMEZONE)

    if created_at.date() == now.date():
        seconds = max((now - created_at).total_seconds(), 0)

        if seconds < 60:
            return "방금 전"
        if seconds < 3600:
            return f"{int(seconds // 60)}분 전"
        return f"{int(seconds // 3600)}시간 전"

    return f"{created_at.year}년 {created_at.month}월 {created_at.day}일"


def load_posts():
    return list(
        get_database()["posts"].find(
            {
                "$or": [
                    {"status": "published"},
                    {"status": {"$exists": False}},
                ]
            },
        )
    )


def filter_posts(posts, period):
    today = datetime.now(SEOUL_TIMEZONE).date()

    def created_date(post):
        return post["created_at"].date()

    if period == "today":
        return [post for post in posts if created_date(post) == today]

    if period == "week":
        week_start = today - timedelta(days=today.weekday())
        return [post for post in posts if created_date(post) >= week_start]
    if period == "month":
        return [
            post
            for post in posts
            if created_date(post).year == today.year
            and created_date(post).month == today.month
        ]

    if period == "year":
        return [post for post in posts if created_date(post).year == today.year]

    return []


def get_sorted_posts(sort_type, period):
    posts = []
    for post in load_posts():
        comments = post.get("comments", 0)
        posts.append(
            {
                **post,
                "id": str(post.get("_id", "")),
                "author": post.get("author") or post.get("user_id", "알 수 없음"),
                "summary": post.get("summary") or post.get("content", "")[:160],
                "tags": post.get("tags", []),
                "likes": post.get("likes", 0),
                "views": post.get("views", 0),
                "views_24h": post.get("views_24h", 0),
                "comment_count": (
                    len(comments) if isinstance(comments, list) else comments
                ),
                "created_at": normalize_created_at(post),
            }
        )

    filtered_posts = filter_posts(posts, period)
    sorted_posts = sorted(filtered_posts, key=SORT_KEYS[sort_type], reverse=True)

    return [
        {
            **post,
            "relative_time": get_relative_time(post["created_at"]),
        }
        for post in sorted_posts
    ]


def render_index(sort_type, period):
    sort_urls = {
        name: (
            url_for("main.sorted_index", sort_type=name)
            if period == "week"
            else url_for("main.filtered_index", sort_type=name, period=period)
        )
        for name in SORT_KEYS
    }
    period_urls = {
        name: (
            url_for("main.sorted_index", sort_type=sort_type)
            if name == "week"
            else url_for("main.filtered_index", sort_type=sort_type, period=name)
        )
        for name in PERIOD_LABELS
    }

    return render_template(
        "main.html",
        posts=get_sorted_posts(sort_type, period),
        current_sort=sort_type,
        current_period=period,
        period_labels=PERIOD_LABELS,
        sort_urls=sort_urls,
        period_urls=period_urls,
    )


@main_bp.route("/")
def index():
    return render_index("trending", "week")


@main_bp.route("/<any(trending,views,likes,latest):sort_type>")
def sorted_index(sort_type):
    return render_index(sort_type, "week")


@main_bp.route(
    "/<any(trending,views,likes,latest):sort_type>"
    "/<any(today,week,month,year):period>"
)
def filtered_index(sort_type, period):
    return render_index(sort_type, period)
