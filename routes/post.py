from flask import Flask, Blueprint, render_template, redirect, url_for, request
from bson.objectid import ObjectId
from .database import db

post_bp = Blueprint("post", __name__)


@post_bp.route('/post/<id>')                            #post 페이지
def view_post(id):
    # DB에서 해당 ID의 post post.html로 전송
    post = db.posts.find_one({'_id': ObjectId(id)})
    return render_template('post.html', post=post)

@post_bp.route('/like/<id>', methods=['POST'])          #좋아요
def like_post(id):
    #likes++ 후 #view post로
    db.posts.update_one({'_id': ObjectId(id)}, {'$inc': {'likes': 1}})
    return redirect(url_for('post.view_post', id=id))

@post_bp.route('/comment/<id>', methods=['POST'])       #댓글
def add_comment(id):
    author = request.form.get('author')
    text = request.form.get('text')
    
    if text:
        #작성 댓글을 comments 리스트에 push
        db.posts.update_one(
            {'_id': ObjectId(id)},
            {'$push': {'comments': {'author': author, 'text': text}}}
        )
    return redirect(url_for('post.view_post', id=id))
