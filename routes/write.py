from datetime import datetime, timezone

from bson.errors import InvalidId
from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for
from bson.objectid import ObjectId
from .database import db

from routes.authority import login_required

write_bp = Blueprint("write", __name__)




# post 데이터 추출 함수
def get_post_form_data():
    #tag #기준으로 분류후 양옆 띄어쓰기 제거
    raw_tags = request.form.get('tags', '')
    tags_list = []
    for t in raw_tags.split('#'):
        stripped_t = t.strip()
        if stripped_t:
            tags_list.append(stripped_t)

    return {
        'title': request.form.get('title'),
        'content': request.form.get('content'),
        'tags': tags_list,
        'summary': request.form.get('summary'),
        'likes': 0,         # 기본값 추가
        'comments': [],      # 기본값 추가
        'current_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
        "user_id": g.user_id,   # user id
        #"author": g.user_id,    기존 화면 호환용, 제거가능
    }

@write_bp.route('/write', methods=['GET', 'POST'])       #새 글 작성
@login_required
def write():
    if request.method == 'POST':
        form_data = get_post_form_data()

        # 태그칸에#만 쓰고 넘기면
        if len(form_data['tags']) == 0:
            flash('태그를 입력해주세요. (예: #1#2)')
            return render_template('write.html', post=form_data)
        
        db.posts.insert_one(form_data)
        return redirect(url_for('main.index'))
        
    return render_template('write.html')

@write_bp.route('/edit/<id>', methods=['GET', 'POST'])   #글 수정
@login_required
def edit(id):
    try:
        object_id = ObjectId(id)
    except InvalidId:
        abort(404)

    # 로그인한 사용자가 작성한 글만 조회 가능
    post = db.posts.find_one({
        "_id": object_id,
        "user_id": g.user_id,
    })
    if not post:
        abort(404)

    #GET으로 기존 글 정보 로드
    if request.method == 'GET':
        post = db.posts.find_one({'_id': ObjectId(id), "user_id": g.user_id})   # user id
        if post and 'tags' in post:
            post['tags_str'] = '#' + ' #'.join(post['tags'])
        return render_template('write.html', post=post)
    #POST로 바뀐 정보 저장
    else:
        form_data = get_post_form_data()   

        # 태그칸에#만 쓰고 넘기면
        if len(form_data['tags']) == 0:
            flash('태그를 입력해주세요. (예: #1#2)')
            post = db.posts.find_one({'_id': ObjectId(id), "user_id": g.user_id})
            if post:
                post.update(form_data)
            return render_template('write.html', post=post)
        
        result = db.posts.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'title': form_data['title'],
                'content': form_data['content'],
                'tags': form_data['tags'],
                'summary': form_data['summary']
            }}
        )

        if result.matched_count == 0:
            return "수정 권한이 없거나 게시글이 없습니다.", 403

        return redirect(url_for("post.view_post", id=id))