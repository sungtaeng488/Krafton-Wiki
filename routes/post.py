from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import Blueprint, abort, redirect, render_template, request, url_for

from db import get_posts_collection

post_bp = Blueprint("post", __name__)


@post_bp.route('/post/<id>')                            #post 페이지
def view_post(id):
    # DB에서 해당 ID의 post post.html로 전송
    try:
        object_id = ObjectId(id)
    except InvalidId:
        abort(404)

    post = get_posts_collection().find_one({'_id': object_id})
    if not post:
        abort(404)

    comments = post.get('comments', [])
    post['comment_count'] = len(comments) if isinstance(comments, list) else comments
    post['comments'] = comments if isinstance(comments, list) else []
    return render_template('post.html', post=post)

@post_bp.route('/like/<id>', methods=['POST'])          #좋아요
def like_post(id):
    #likes++ 후 #view post로
    get_posts_collection().update_one(
        {'_id': ObjectId(id)},
        {'$inc': {'likes': 1}},
    )
    return redirect(url_for('post.view_post', id=id))

@post_bp.route('/comment/<id>', methods=['POST'])       #댓글
def add_comment(id):
    author = request.form.get('author')
    text = request.form.get('text')

    if text:
        #작성 댓글을 comments 리스트에 push
        posts = get_posts_collection()
        object_id = ObjectId(id)
        post = posts.find_one({'_id': object_id}, {'comments': 1})
        if post and not isinstance(post.get('comments', []), list):
            posts.update_one({'_id': object_id}, {'$set': {'comments': []}})

        posts.update_one(
            {'_id': object_id},
            {'$push': {'comments': {'author': author, 'text': text}}}
        )
    return redirect(url_for('post.view_post', id=id))
