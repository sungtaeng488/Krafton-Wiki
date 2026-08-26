from flask import Flask, request, Blueprint, render_template, flash, redirect, url_for, g
from bson.objectid import ObjectId
from datetime import datetime
from .database import db
from .authority import login_required

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
        'author': g.user_id,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'likes': 0,         # 기본값 추가
        'liked_users': [],
        'dislikes': 0,      
        'comments': [],
        'views':0,
        'views_24h':[]
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
    #GET으로 기존 글 정보 로드
    if request.method == 'GET':
        post = db.posts.find_one({'_id': ObjectId(id)})
        if post and 'tags' in post:
            post['tags_str'] = '#' + ' #'.join(post['tags'])
        return render_template('write.html', post=post)
    #POST로 바뀐 정보 저장
    else:
        form_data = get_post_form_data()   

        # 태그칸에#만 쓰고 넘기면
        if len(form_data['tags']) == 0:
            flash('태그를 입력해주세요. (예: #1#2)')
            post = db.posts.find_one({'_id': ObjectId(id)})
            if post:
                post.update(form_data)
            return render_template('write.html', post=post)
        
        db.posts.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'title': form_data['title'],
                'content': form_data['content'],
                'tags': form_data['tags'],
                'summary': form_data['summary']
            }}
)
        return redirect(url_for('search.search'))

@write_bp.route('/delete/<id>', methods=['POST'])           # 글 삭제
@login_required
def delete(id):
    # 삭제하려는 글을 DB에서 찾기
    post = db.posts.find_one({'_id': ObjectId(id)})
    
    # 글이 존재하고, 현재 로그인한 사용자(g.user_id)가 글의 작성자와 일치하는지 확인
    if post and post.get('author') == g.user_id:
        db.posts.delete_one({'_id': ObjectId(id)})
        flash('글이 성공적으로 삭제되었습니다.')
    else:
        flash('삭제 권한이 없거나 존재하지 않는 글입니다.')

    return redirect(url_for('search.search', tag=request.form.get('search_tag')))