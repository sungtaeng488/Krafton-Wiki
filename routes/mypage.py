from datetime import datetime, timezone
from uuid import uuid4

from bson import ObjectId
from bson.errors import InvalidId
from flask import Blueprint, abort, g, redirect, render_template, request, url_for

from db import get_post_histories_collection, get_posts_collection
from db.post_history import ensure_initial_post_history, save_post_history
from routes.authority import login_required


# 마이페이지와 내 게시글 관련 라우트를 담는 Blueprint
mypage_bp = Blueprint("mypage", __name__)


@mypage_bp.route("/mypage")
@login_required
def mypage():
    # 내정보

    # 유저가 작성한 포스트만 조회
    posts = list(get_posts_collection().find({"user_id": g.user_id}))
    for post in posts:
        created_at = post.get("created_at")
        if isinstance(created_at, datetime):
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            post["created_at_text"] = created_at.strftime("%Y.%m.%d")

    return render_template("mypage.html", user_id=g.user_id, posts=posts)

# 임시
@mypage_bp.route("/mypage/posts/new", methods=["GET", "POST"])
@login_required
def create_post():
    # GET 요청: 새 글 작성 화면
    if request.method == "GET":
        return render_template("post_create.html")

    # POST 요청: 제목과 내용 받아서 DB에 저장
    title_receive = request.form.get("title_give", "").strip()
    content_receive = request.form.get("content_give", "").strip()
    if not title_receive or not content_receive:
        return render_template(
            "post_create.html",
            error="제목과 내용을 모두 입력해주세요.",
        ), 400

    now = datetime.now(timezone.utc)
    post_document = {
            "slug": uuid4().hex,
            "title": title_receive,
            "summary": content_receive[:160],
            "content": content_receive,
            "tags": [],
            "author": g.user_id,
            "user_id": g.user_id,
            "created_at": now,
            "updated_at": now,
            "status": "published",
            "views": 0,
            "views_24h": 0,
            "likes": 0,
            "comments": [],
            "version": 1,
        }
    result = get_posts_collection().insert_one(post_document)
    save_post_history(
        result.inserted_id,
        1,
        post_document,
        g.user_id,
        now,
    )

    return redirect(url_for("mypage.mypage"))


@mypage_bp.route("/mypage/<post_id>/edit", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    try:
        object_id = ObjectId(post_id)
    except InvalidId:
        abort(404)

    # 다른 사용자의 글은 수정 화면에서도 조회할 수 없음
    posts_collection = get_posts_collection()
    post = posts_collection.find_one({"_id": object_id, "user_id": g.user_id})
    if not post:
        abort(404)

    # GET 요청: 기존 내용이 채워진 수정 화면
    if request.method == "GET":
        return render_template("post_edit.html", post=post)

    title_receive = request.form.get("title_give", "").strip()
    content_receive = request.form.get("content_give", "").strip()
    if not title_receive or not content_receive:
        return render_template(
            "post_edit.html",
            post=post,
            error="제목과 내용을 모두 입력해주세요.",
        ), 400

    current_version = ensure_initial_post_history(post, posts_collection)
    new_version = current_version + 1
    updated_at = datetime.now(timezone.utc)
    result = posts_collection.update_one(
        {
            "_id": object_id,
            "user_id": g.user_id,
            "version": current_version,
        },
        {
            "$set": {
                "title": title_receive,
                "content": content_receive,
                "updated_at": updated_at,
                "version": new_version,
            }
        },
    )

    if result.matched_count == 0:  # 1인 경우 내 글을 찾았고 수정 권한이 있음
        return "다른 수정이 먼저 반영되었습니다. 다시 시도해주세요.", 409

    save_post_history(
        object_id,
        new_version,
        {**post, "title": title_receive, "content": content_receive},
        g.user_id,
        updated_at,
    )

    return redirect(url_for("mypage.mypage"))


@mypage_bp.route("/mypage/<post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    try:
        object_id = ObjectId(post_id)
    except InvalidId:
        abort(404)

    result = get_posts_collection().delete_one(
        {
            "_id": object_id,
            "user_id": g.user_id,
        }
    )

    if result.deleted_count == 0:
        return "삭제 권한이 없거나 게시글이 없습니다.", 403

    get_post_histories_collection().delete_many({"post_id": object_id})

    return redirect(url_for("mypage.mypage"))
