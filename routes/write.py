from datetime import datetime, timezone
from uuid import uuid4

from bson.errors import InvalidId
from bson.objectid import ObjectId
from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from db import get_posts_collection
from db.post_history import ensure_initial_post_history, save_post_history
from routes.authority import login_required

import re

write_bp = Blueprint("write", __name__)




# post 데이터 추출 함수
def get_post_form_data():
    
    raw_tags = request.form.get('tags', '')
    #정규표현식으로 태그 분리
    tags_list = re.findall(r'#(\w+(?:#(?!\w)|\+\+)?)', raw_tags)

    now = datetime.now(timezone.utc)
    author = g.user_id

    return {
        'title': request.form.get('title', '').strip(),
        'content': request.form.get('content', '').strip(),
        'tags': tags_list,
        'summary': request.form.get('summary', '').strip(),
        'author': author,
        'user_id': author,
        'updated_at': now,
    }

@write_bp.route('/write', methods=['GET', 'POST'])       #새 글 작성
@login_required
def write():
    if request.method == 'POST':
        form_data = get_post_form_data()

        form_data.update(
            {
                'slug': uuid4().hex,
                'created_at': form_data['updated_at'],
                'status': 'published',
                'likes': 0,
                'liked_users': [],
                'dislikes': 0,
                'disliked_users': [],
                'comments': [],
                'views': 0,
                'views_24h': 0,
                'version': 1,
            }
        )
        result = get_posts_collection().insert_one(form_data)
        save_post_history(
            result.inserted_id,
            1,
            form_data,
            g.user_id,
            form_data['created_at'],
        )
        return redirect(url_for('main.index'))

    return render_template('write.html')

@write_bp.route('/edit/<id>', methods=['GET', 'POST'])   #글 수정
@login_required
def edit(id):
    try:
        object_id = ObjectId(id)
    except InvalidId:
        abort(404)

    posts = get_posts_collection()
    post = posts.find_one({'_id': object_id})
    if not post:
        abort(404)

    owner_id = post.get('user_id') or post.get('author')
    if owner_id != g.user_id:
        abort(403)

    #GET으로 기존 글 정보 로드
    if request.method == 'GET':
        if 'tags' in post:
            post['tags_str'] = '#' + ' #'.join(post['tags'])
        return render_template('write.html', post=post)
    #POST로 바뀐 정보 저장
    else:
        form_data = get_post_form_data()

        # 태그칸에#만 쓰고 넘기면
        if len(form_data['tags']) == 0:
            flash('태그를 입력해주세요. (예: #1#2)')
            post.update(form_data)
            post['tags_str'] = '#' + ' #'.join(form_data['tags'])
            return render_template('write.html', post=post)

        is_changed = (
            post.get('title') != form_data['title'] or
            post.get('content') != form_data['content'] or
            post.get('summary') != form_data['summary'] or
            post.get('tags') != form_data['tags']
        )

        if not is_changed:
            flash('변경된 내용이 없습니다.')
            return redirect(url_for('write.edit', id=id))

        current_version = ensure_initial_post_history(post, posts)
        new_version = current_version + 1
        result = posts.update_one(
            {
                '_id': object_id,
                'version': current_version,
                '$or': [
                    {'user_id': g.user_id},
                    {'user_id': {'$exists': False}, 'author': g.user_id},
                ],
            },
            {'$set': {
                'title': form_data['title'],
                'content': form_data['content'],
                'tags': form_data['tags'],
                'summary': form_data['summary'],
                'updated_at': form_data['updated_at'],
                'version': new_version,
            }}
        )
        if result.matched_count == 0:
            abort(409)

        save_post_history(
            object_id,
            new_version,
            {**post, **form_data},
            g.user_id,
            form_data['updated_at'],
        )

        return redirect(url_for('post.view_post', id=id))
