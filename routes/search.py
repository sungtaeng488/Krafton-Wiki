import re

from flask import Blueprint, render_template, request

from db import get_posts_collection

search_bp = Blueprint("search", __name__)


def build_tag_query(search_tag):
    """쉼표(AND), 파이프(OR), 하이픈(NOT) 검색 문법을 MongoDB 쿼리로 변환."""
    conditions = [{"status": "published"}]

    for and_part in search_tag.split(","):
        terms = [term.strip() for term in and_part.split("|") if term.strip()]
        positive_conditions = []

        for term in terms:
            if term.startswith("-"):
                excluded_tag = term[1:].strip()
                if excluded_tag:
                    conditions.append(
                        {"tags": {"$not": re.compile(re.escape(excluded_tag), re.IGNORECASE)}}
                    )
            else:
                positive_conditions.append(
                    {"tags": re.compile(re.escape(term), re.IGNORECASE)}
                )

        if len(positive_conditions) == 1:
            conditions.append(positive_conditions[0])
        elif positive_conditions:
            conditions.append({"$or": positive_conditions})

    return conditions[0] if len(conditions) == 1 else {"$and": conditions}


@search_bp.route('/search')                                     #검색 페이지
def search():
    # url에서 검색어 추출
    search_tag = request.args.get('tag')

    if search_tag:
        posts = list(
            get_posts_collection().find(
                build_tag_query(search_tag)
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
