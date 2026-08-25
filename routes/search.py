from flask import Flask, request, Blueprint, render_template
from .database import db

search_bp = Blueprint("search", __name__)

@search_bp.route('/search')                                     #검색 페이지
def search():
    # url에서 검색어 추출
    search_tag = request.args.get('tag')
    
    if search_tag:
        posts = list(db.posts.find({'tags': search_tag}))
    else:
        # 검색어 없으면 전체 글 로드
        posts = []
        
    return render_template('search.html', posts=posts, search_tag=search_tag)
