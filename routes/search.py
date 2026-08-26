from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import re
from flask import Blueprint, render_template, request

from db import get_posts_collection

search_bp = Blueprint("search", __name__)
SEOUL_TIMEZONE = ZoneInfo("Asia/Seoul")

def as_seoul_datetime(value):
    if value.tzinfo is None:
        return value.replace(tzinfo=SEOUL_TIMEZONE)
    return value.astimezone(SEOUL_TIMEZONE)

def normalize_created_at(post):
    created_at = post.get("created_at") or post.get("updated_at")
    if isinstance(created_at, str):
        try:
            created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M")
        except ValueError:
            created_at = None
    if created_at is None:
        created_at = datetime.min.replace(tzinfo=SEOUL_TIMEZONE)
    return as_seoul_datetime(created_at)


def get_relative_time(created_at):
    created_at = as_seoul_datetime(created_at)
    now = datetime.now(SEOUL_TIMEZONE)

    if created_at.date() == now.date():
        seconds = max((now - created_at).total_seconds(), 0)
        if seconds < 60:
            return "방금 전"
        if seconds < 3600:
            return f"{int(seconds // 60)}분 전"
        return f"{int(seconds // 3600)}시간 전"

    return f"{created_at.year}년 {created_at.month}월 {created_at.day}일"

def build_tag_query(search_tag):
    """쉼표(AND), 파이프(OR), 하이픈(NOT) 검색 문법을 MongoDB 쿼리로 변환."""
    conditions = [{"status": "published"}]
    # ,(AND) 기준으로 split
    for and_part in search_tag.split(","):
        # |(OR) 기준으로 split
        terms = [term.strip() for term in and_part.split("|") if term.strip()]
        positive_conditions = []
        # -(NOT) 처리
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


@search_bp.route('/search')
def search():
    # 검색어 및 정렬 기준 추출 (기본값 'likes')
    search_tag = request.args.get('tag')
    sort_type = request.args.get('sort', 'likes') 

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

            normalized_date = normalize_created_at(post)
            post['created_at'] = normalized_date
            post['relative_time'] = get_relative_time(normalized_date)
            
        if sort_type == 'likes':
            posts.sort(key=lambda post: post.get('likes', 0), reverse=True)
        elif sort_type == 'views':
            posts.sort(key=lambda post: post.get('views', 0), reverse=True)
        elif sort_type == 'comments':
            posts.sort(key=lambda post: post.get('comment_count', 0), reverse=True)
        else:
            posts.sort(key=lambda post: post.get('created_at', ''), reverse=True)

        # 싫어요가 5개 이상인 글을 리스트 맨 아래로 밀어냄
        posts.sort(key=lambda post: post.get('dislikes', 0) >= 5)

    else:
        # 검색어 없으면 전체 글 로드
        posts = []

    return render_template(
        'search.html', 
        posts=posts, 
        search_tag=search_tag, 
        current_sort=sort_type
    )
