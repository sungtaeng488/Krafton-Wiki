from pymongo import MongoClient


# MongoDB 공통 연결
# client = MongoClient("mongodb://test:test@localhost", 27017)
client = MongoClient("localhost", 27017)
db = client.krafton_wiki

# 컬렉션별 공통 접근 변수
users_collection = db.users
posts_collection = db.posts

# 회원가입 시 같은 ID가 중복 저장되지 않도록 설정
users_collection.create_index("user_id", unique=True)
