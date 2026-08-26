from datetime import datetime, timezone
from uuid import uuid4
from zoneinfo import ZoneInfo

from bson.errors import InvalidId
from bson.objectid import ObjectId
from flask import (
    Blueprint,
    abort,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from pymongo import ReturnDocument

from db import get_post_histories_collection, get_posts_collection
from db.post_history import (
    ensure_initial_post_history,
    get_post_history,
    list_post_histories,
)
from routes.authority import login_required


post_bp = Blueprint("post", __name__)
SEOUL_TIMEZONE = ZoneInfo("Asia/Seoul")


def parse_post_id(post_id):
    try:
        return ObjectId(post_id)
    except InvalidId:
        abort(404)


def format_datetime(value):
    if not isinstance(value, datetime):
        return ""

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    return value.astimezone(SEOUL_TIMEZONE).strftime("%Y년 %m월 %d일 %H:%M")


def format_date(value):
    if not isinstance(value, datetime):
        return ""

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    return value.astimezone(SEOUL_TIMEZONE).strftime("%Y년 %m월 %d일")


def normalize_comments(posts, post):
    """기존 댓글에도 수정·삭제·좋아요에 필요한 필드를 한 번 보완."""
    comments = post.get("comments", [])
    if not isinstance(comments, list):
        return [], comments or 0

    normalized = []
    changed = False
    for value in comments:
        if not isinstance(value, dict):
            changed = True
            continue

        comment = {**value}
        if not comment.get("id"):
            comment["id"] = uuid4().hex
            changed = True
        if not isinstance(comment.get("likes"), int):
            comment["likes"] = 0
            changed = True

        normalized.append(comment)

    if changed:
        posts.update_one(
            {"_id": post["_id"]},
            {"$set": {"comments": normalized}},
        )

    return normalized, len(normalized)


@post_bp.route("/post/<id>")
def view_post(id):
    object_id = parse_post_id(id)
    posts = get_posts_collection()
    post = posts.find_one_and_update(
        {"_id": object_id},
        {"$inc": {"views": 1}},
        return_document=ReturnDocument.AFTER,
    )
    if not post:
        abort(404)

    post["comments"], post["comment_count"] = normalize_comments(posts, post)
    post["owner_id"] = post.get("user_id") or post.get("author")
    post["created_at_text"] = format_datetime(post.get("created_at"))
    post["updated_at_text"] = format_datetime(post.get("updated_at"))

    for comment in post["comments"]:
        if isinstance(comment, dict):
            comment["created_at_text"] = format_datetime(comment.get("created_at"))

    return render_template("post.html", post=post)


@post_bp.route("/post/<id>/history")
@post_bp.route("/post/<id>/history/<int:version>")
def view_history(id, version=None):
    object_id = parse_post_id(id)
    posts = get_posts_collection()
    post = posts.find_one({"_id": object_id})
    if not post:
        abort(404)

    current_version = ensure_initial_post_history(post, posts)
    histories = list_post_histories(object_id)
    for history in histories:
        history["created_at_text"] = format_datetime(history.get("created_at"))

    selected_history = None
    if version is not None:
        selected_history = get_post_history(object_id, version)
        if not selected_history:
            abort(404)
        selected_history["created_at_text"] = format_datetime(
            selected_history.get("created_at")
        )
        selected_history["created_date_text"] = format_date(
            selected_history.get("created_at")
        )

    return render_template(
        "post_history.html",
        post=post,
        histories=histories,
        selected_history=selected_history,
        current_version=current_version,
    )


@post_bp.route("/like/<id>", methods=["POST"])
@login_required
def like_post(id):
    object_id = parse_post_id(id)
    posts = get_posts_collection()
    result = posts.update_one(
        {"_id": object_id, "liked_users": g.user_id},
        {
            "$pull": {"liked_users": g.user_id},
            "$inc": {"likes": -1},
        },
    )
    if result.modified_count == 0:
        result = posts.update_one(
            {"_id": object_id},
            {
                "$addToSet": {"liked_users": g.user_id},
                "$inc": {"likes": 1},
            },
        )
        if result.matched_count == 0:
            abort(404)

    return redirect(url_for("post.view_post", id=id))

@post_bp.route('/dislike/<id>', methods=['POST'])          #싫어요
@login_required
def dislike_post(id):
    object_id = parse_post_id(id)
    posts = get_posts_collection()
    result = posts.update_one(
        {"_id": object_id, "disliked_users": g.user_id},
        {
            "$pull": {"disliked_users": g.user_id},
            "$inc": {"dislikes": -1},
        },
    )
    if result.modified_count == 0:
        result = posts.update_one(
            {"_id": object_id},
            {
                "$addToSet": {"disliked_users": g.user_id},
                "$inc": {"dislikes": 1},
            },
        )
        if result.matched_count == 0:
            abort(404)
        
    return redirect(url_for("post.view_post", id=id))


@post_bp.route("/comment/<id>", methods=["POST"])
@login_required
def add_comment(id):
    object_id = parse_post_id(id)
    text = request.form.get("text", "").strip()
    if not text:
        return redirect(url_for("post.view_post", id=id))

    posts = get_posts_collection()
    post = posts.find_one({"_id": object_id}, {"comments": 1})
    if not post:
        abort(404)

    if not isinstance(post.get("comments", []), list):
        posts.update_one({"_id": object_id}, {"$set": {"comments": []}})

    posts.update_one(
        {"_id": object_id},
        {
            "$push": {
                "comments": {
                    "id": uuid4().hex,
                    "author": g.user_id,
                    "text": text,
                    "likes": 0,
                    "created_at": datetime.now(timezone.utc),
                }
            }
        },
    )
    return redirect(url_for("post.view_post", id=id))


@post_bp.route("/post/<id>/comments/<comment_id>/like", methods=["POST"])
@login_required
def like_comment(id, comment_id):
    object_id = parse_post_id(id)
    posts = get_posts_collection()
    result = posts.update_one(
        {"_id": object_id, "comments.id": comment_id},
        {"$inc": {"comments.$.likes": 1}},
    )
    if result.matched_count == 0:
        return jsonify(error="댓글을 찾을 수 없습니다."), 404

    post = posts.find_one(
        {"_id": object_id, "comments.id": comment_id},
        {"comments": 1},
    )
    comment = next(
        item for item in post["comments"] if item.get("id") == comment_id
    )
    return jsonify(ok=True, likes=comment.get("likes", 0))


@post_bp.route("/post/<id>/comments/<comment_id>", methods=["PATCH"])
@login_required
def update_comment(id, comment_id):
    object_id = parse_post_id(id)
    payload = request.get_json(silent=True) or {}
    text = str(payload.get("text", "")).strip()
    if not text:
        return jsonify(error="댓글 내용을 입력해주세요."), 400
    if len(text) > 1000:
        return jsonify(error="댓글은 최대 1,000자까지 작성할 수 있습니다."), 400

    result = get_posts_collection().update_one(
        {
            "_id": object_id,
            "comments": {
                "$elemMatch": {"id": comment_id, "author": g.user_id}
            },
        },
        {
            "$set": {
                "comments.$.text": text,
                "comments.$.updated_at": datetime.now(timezone.utc),
            }
        },
    )
    if result.matched_count == 0:
        return jsonify(error="댓글 수정 권한이 없거나 댓글이 없습니다."), 403

    return jsonify(ok=True, text=text)


@post_bp.route("/post/<id>/comments/<comment_id>", methods=["DELETE"])
@login_required
def delete_comment(id, comment_id):
    object_id = parse_post_id(id)
    posts = get_posts_collection()
    result = posts.update_one(
        {"_id": object_id},
        {
            "$pull": {
                "comments": {"id": comment_id, "author": g.user_id}
            }
        },
    )
    if result.modified_count == 0:
        return jsonify(error="댓글 삭제 권한이 없거나 댓글이 없습니다."), 403

    post = posts.find_one({"_id": object_id}, {"comments": 1})
    return jsonify(ok=True, comment_count=len(post.get("comments", [])))


@post_bp.route("/post/<id>/delete", methods=["POST"])
@login_required
def delete_post(id):
    object_id = parse_post_id(id)
    posts = get_posts_collection()
    post = posts.find_one({"_id": object_id}, {"user_id": 1, "author": 1})
    if not post:
        abort(404)

    owner_id = post.get("user_id") or post.get("author")
    if owner_id != g.user_id:
        abort(403)

    result = posts.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        abort(404)

    get_post_histories_collection().delete_many({"post_id": object_id})

    return redirect(url_for("main.index"))
