from flask import Flask, Blueprint, render_template, redirect, url_for, request, g
from bson.objectid import ObjectId
from .database import db
from .authority import login_required

post_bp = Blueprint("post", __name__)


@post_bp.route('/post/<id>')                            #post 페이지
def view_post(id):
    # DB에서 해당 ID의 post를 post.html로 전송
    post = db.posts.find_one({'_id': ObjectId(id)})
    return render_template('post.html', post=post)

@post_bp.route('/like/<id>', methods=['POST'])          #좋아요
@login_required
def like_post(id):
    user_id = g.user_id

    # 이미 좋아요를 눌렀으면 likes--
    # '_id'일치하고 'liked_users' 안에 user_id가 있는 문서만 찾아서 업데이트
    result = db.posts.update_one(
        {'_id': ObjectId(id), 'liked_users': user_id},
        {
            '$pull': {'liked_users': user_id},
            '$inc': {'likes': -1}
        }
    )

    # 업데이트된 문서가 없으면
    if result.modified_count == 0:
        # user_id 추가 후 likes++
        db.posts.update_one(
            {'_id': ObjectId(id)},
            {
                '$addToSet': {'liked_users': user_id},
                '$inc': {'likes': 1}
            }
        )

    return redirect(url_for('post.view_post', id=id))

@post_bp.route('/comment/<id>', methods=['POST'])       #댓글
@login_required
def add_comment(id):
    author = g.user_id
    text = request.form.get('text')
    
    if text:
        #댓글 고유 ID 생성
        comment_id = str(ObjectId()) 
        #작성 댓글을 comments 리스트에 push
        db.posts.update_one(
            {'_id': ObjectId(id)},
            {'$push': {'comments': {'comment_id': comment_id, 'author': author, 'text': text}}}
        )
    return redirect(url_for('post.view_post', id=id))

@post_bp.route('/comment/delete/<post_id>/<comment_id>', methods=['POST'])
@login_required
def delete_comment(post_id, comment_id):
    #omments 배열에서 comment_id와 author가 일치하는 항목 삭제
    db.posts.update_one(
        {'_id': ObjectId(post_id)},
        {'$pull': {
            'comments': {
                'comment_id': comment_id, 
                'author': g.user_id
            }
        }}
    )
    return redirect(url_for('post.view_post', id=post_id))

@post_bp.route('/comment/edit/<post_id>/<comment_id>', methods=['POST'])
@login_required
def edit_comment(post_id, comment_id):
    new_text = request.form.get('text')
    
    if new_text:
        # 조건: 해당 게시글 안에서, comment_id가 일치하고, 작성자가 본인인 댓글을 찾음
        db.posts.update_one({
                '_id': ObjectId(post_id),
                'comments.comment_id': comment_id,
                'comments.author': g.user_id},
            # $==위 조건에서 찾은 댓글의 위치(인덱스)
            {'$set': {'comments.$.text': new_text}}
        )
        
    return redirect(url_for('post.view_post', id=post_id))