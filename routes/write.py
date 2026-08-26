from flask import Flask, request, Blueprint, render_template, flash, redirect, url_for
from bson.objectid import ObjectId
from datetime import datetime
from .database import db

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
        'author': request.form.get('author')
    }

@write_bp.route('/write', methods=['GET', 'POST'])       #새 글 작성
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