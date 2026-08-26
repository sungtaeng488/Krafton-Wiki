from datetime import datetime, timezone

from flask import Blueprint, g, render_template

from db import get_posts_collection


# 마이페이지와 내 게시글 관련 라우트를 담는 Blueprint
someonepage_bp = Blueprint("someonepage", __name__)


@someonepage_bp.route("/someonepage/<other_user_id>")
def someonepage(other_user_id):
    # 내정보

    # 유저가 작성한 포스트만 조회
    posts = list(get_posts_collection().find({"user_id": other_user_id}))
    for post in posts:
        created_at = post.get("created_at")
        if isinstance(created_at, datetime):
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            post["created_at_text"] = created_at.strftime("%Y.%m.%d")

    return render_template("someonepage.html", user_id=other_user_id, posts=posts)
