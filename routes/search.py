from flask import Flask, request, Blueprint, render_template
from .database import db
import re

search_bp = Blueprint("search", __name__)

@search_bp.route('/search')                                     #검색 페이지
def search():
    # 검색어 추출
    search_tag = request.args.get('tag')
    
    if search_tag:
        and_conditions = []
        
        #,(AND) 기준으로 split
        for and_part in search_tag.split(','):
            or_conditions = []
            
            # |(OR) 기준으로 split
            for term in and_part.split('|'):
                term = term.strip()
                if not term:
                    continue
                
                # -(NOT) 처리
                if term.startswith('-'):
                    word = term[1:].strip() 
                    if word:
                        # 해당 단어가 포함되지 않은 경우 ($not)
                        or_conditions.append({'tags': {'$not': re.compile(word, re.IGNORECASE)}})
                else:
                    # 일반 검색어인 경우 ($regex)
                    or_conditions.append({'tags': {'$regex': re.compile(term, re.IGNORECASE)}})
            
            # OR 묶음이 완성되면 AND 리스트에 추가
            if or_conditions:
                # 항목이 1개면 그대로 넣고, 2개 이상이면 $or로 묶어서 넣기
                if len(or_conditions) == 1:
                    and_conditions.append(or_conditions[0])
                else:
                    and_conditions.append({'$or': or_conditions})
                    
        #쿼리 완성 및 검색
        if and_conditions:
            # 전체 묶음이 1개면 그대로, 여러 개면 $and로 묶어서 검색
            query = and_conditions[0] if len(and_conditions) == 1 else {'$and': and_conditions}
            posts = list(db.posts.find(query))
        else:
            posts = []
            
    else:
        # 검색어가 없으면 빈칸
        posts = []
        
    return render_template('search.html', posts=posts, search_tag=search_tag)