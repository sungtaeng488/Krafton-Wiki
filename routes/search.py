from flask import Blueprint, render_template, request

from db import get_posts_collection

search_bp = Blueprint("search", __name__)

@search_bp.route('/search')                                     #검색 페이지
def search():
    # url에서 검색어 추출
    search_tag = request.args.get('tag')

    if search_tag:
        posts = list(
            get_posts_collection().find(
                {'tags': search_tag, 'status': 'published'}
            )
        )
        for post in posts:
            comments = post.get('comments', 0)
            post['comment_count'] = (
                len(comments) if isinstance(comments, list) else comments
            )
    else:
        # 검색어 없으면 전체 글 로드
        posts = []

    return render_template('search.html', posts=posts, search_tag=search_tag)
