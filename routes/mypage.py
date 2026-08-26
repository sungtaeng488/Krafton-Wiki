from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from flask import Blueprint, abort, g, redirect, render_template, request, url_for

from data.database import posts_collection
from routes.authority import login_required


# 마이페이지와 내 게시글 관련 라우트를 담는 Blueprint
mypage_bp = Blueprint("mypage", __name__)


@mypage_bp.route("/mypage")
@login_required
def mypage():
    # 내정보

    # 유저가 작성한 포스트만 조회
    posts = list(posts_collection.find({"user_id": g.user_id}))

    return render_template("mypage.html", user_id=g.user_id, posts=posts)




@mypage_bp.route("/mypage/<post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    try:
        object_id = ObjectId(post_id)
    except InvalidId:
        abort(404)

    result = posts_collection.delete_one(
        {
            "_id": object_id,
            "user_id": g.user_id,
        }
    )

    if result.deleted_count == 0:
        return "삭제 권한이 없거나 게시글이 없습니다.", 403

    return redirect(url_for("mypage.mypage"))
