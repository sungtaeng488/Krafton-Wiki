from datetime import datetime

from flask import Blueprint, render_template, request

from data.mock_posts import MOCK_POSTS


main_bp = Blueprint("main", __name__)


def get_relative_time(created_at):
    diff = datetime.now() - created_at
    seconds = diff.total_seconds()

    if seconds < 60:
        return "방금 전"
    if seconds < 3600:
        return f"{int(seconds // 60)}분 전"
    if seconds < 86400:
        return f"{int(seconds // 3600)}시간 전"
    if diff.days < 7:
        return f"{diff.days}일 전"

    return created_at.strftime("%Y.%m.%d")


def get_sorted_posts(sort_type):
    sort_keys = {
        "views": lambda post: post["views"],
        "likes": lambda post: post["likes"],
        "latest": lambda post: post["created_at"],
        "trending": lambda post: post["views_24h"] + post["likes"] * 3,
    }
    sort_key = sort_keys.get(sort_type, sort_keys["trending"])
    sorted_posts = sorted(MOCK_POSTS, key=sort_key, reverse=True)

    return [
        {**post, "relative_time": get_relative_time(post["created_at"])}
        for post in sorted_posts
    ]


@main_bp.route("/")
def index():
    sort_type = request.args.get("sort", "trending")
    return render_template(
        "main.html",
        posts=get_sorted_posts(sort_type),
        current_sort=sort_type,
    )
