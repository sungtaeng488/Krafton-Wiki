# JWT
import os                                           # .env에서 JWT 비밀키 read
from datetime import datetime, timedelta, timezone  # JWT의 발급시각, 만료시각
from functools import wraps                         # 로그인 검증 기능

import jwt                                          # PyJWT
from dotenv import load_dotenv                      # .env파일 읽기

from flask import Flask, g, make_response, redirect, render_template, request, url_for
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from werkzeug.security import check_password_hash, generate_password_hash

from routes.main import main_bp

load_dotenv()

app = Flask(__name__)
app.register_blueprint(main_bp)

app.config["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", "development-only-secret-change-before-deploy"
)
app.config["JWT_EXPIRES_MINUTES"] = 60
app.config["JWT_COOKIE_SECURE"] = (
    os.environ.get("JWT_COOKIE_SECURE", "false").lower() == "true"
)

# client = MongoClient("mongodb://test:test@localhost", 27017)
client = MongoClient("localhost", 27017)
db = client.krafton_wiki
users_collection = db.users
users_collection.create_index("user_id", unique=True)

# id 찾는 함수
def load_user_id():
    g.user_id = None

    # 
    token = request.cookies.get("access_token" )
    if not token:
        return          # 아무것도 없으면 route함수 실행

    # JWT 디코딩해서 id찾기
    try:
        g.user_id = jwt.decode(
            token,
            app.config["JWT_SECRET_KEY"],
            algorithms=["HS256"],
        )["sub"]
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError):
        g.user_id = None

# HTTP요청이 왔을 때 route함수보다 먼저 실행
@app.before_request
def set_current_user():
    load_user_id()

# rendre_tempalte()로 HTML을 렌더링할 때 모든 HTML에 공통변수 전달
@app.context_processor
def inject_current_user():
    return {
        "load_user_id": getattr(g, "user_id", None)
    }

# 로그인 검증 함수, 비로그인시 로그인 화면으로
def login_required(function):
    @wraps(function)                                # 원래 함수 정보를 유지
    def wrapped_view(*args, **kwargs):              # 원래 페이지 함수가 받을 수 있는 모든 인자

        token = request.cookies.get("access_token") # 쿠키에서 JWT 문자열을 가져옴
        if not token:                               # JWT가 없으면 로그인하지 않음
            return redirect(url_for("login"))       # 로그인 화면으로

        try:
            g.user_id = jwt.decode(                 # JWT 디코딩, g는 flask가 제공하는 임시 저장 공간
                token,
                app.config["JWT_SECRET_KEY"], 
                algorithms=["HS256"]
            )["sub"]                                # JWT의 sub값 (여기서는 ID)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError):    # exp 만료, JWT 형식이 올바른지, sub값이 없는지
            response = make_response(redirect(url_for("login")))
            response.delete_cookie("access_token")                              # 쿠키 삭제
            return response

        return function(*args, **kwargs)

    return wrapped_view

@app.route("/")
def main():
    return render_template("main.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", registered=request.args.get("registered"))

    # id 또는 비밀번호가 없는 경우
    user_id = request.form.get("id_give", "").strip()
    password = request.form.get("password_give", "")
    if not user_id or not password:
        return render_template("login.html", error="아이디와 비밀번호를 입력해주세요."), 400

    # id가 없거나 비밀번호가 틀린경우
    user = users_collection.find_one({"user_id": user_id})
    if not user or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error="아이디 또는 비밀번호가 올바르지 않습니다."), 401

    # jwt 생성
    token = jwt.encode(
        {
            "sub": user_id,
            "iat": datetime.now(timezone.utc),  # JWT 발급 시각
            "exp": datetime.now(timezone.utc) + timedelta(minutes=app.config["JWT_EXPIRES_MINUTES"]),   # JWT 만료 시간
        },
        app.config["JWT_SECRET_KEY"],
        algorithm="HS256",                      # 서버의 비밀 키로 JWT에 서명
    )

    # 로그인 성공 후 쿠키 발급
    response = make_response(redirect(url_for("main"))) # 쿠키 검증 성공 시 main
    response.set_cookie(
        "access_token",
        token,
        max_age=app.config["JWT_EXPIRES_MINUTES"] * 60, # 브라우저 쿠키 유지 시간
        httponly=True,                                  # 브라우저의 JS가 쿠키를 직접 읽기 어렵게 해 XSS공격 방어
        secure=app.config["JWT_COOKIE_SECURE"],
        samesite="Lax",                                 # 외부 사이트에서 쿠키 요청시(POST) 보내지 않음(보안), 일부 GET에는 보냄
    )
    return response


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    # id, pw받기
    user_id = request.form.get("id_give", "").strip()
    password = request.form.get("password_give", "")
    if not user_id or not password:
        return render_template("signup.html", error="아이디와 비밀번호를 입력해주세요."), 400

    # DB에 넣을 데이터
    user = {
        "user_id": user_id,
        "password_hash": generate_password_hash(password),
    }

    # 중복 검증
    try:
        users_collection.insert_one(user)
    except DuplicateKeyError:
        return render_template("signup.html", error="이미 사용 중인 ID입니다."), 409

    return redirect(url_for("login", registered="1"))


@app.route("/logout", methods=["POST"])
def logout():
    response = make_response(redirect(url_for("login")))
    response.delete_cookie("access_token")
    return response


@app.route("/mypage")
@login_required
def mypage():
    return render_template("mypage.html", user_id=g.user_id)


@app.route("/keyword/<keyword>")
def detail(keyword):
    return render_template("detail.html", keyword=keyword)


@app.route("/quiz/<keyword>")
def quiz(keyword):
    return render_template("quiz.html", keyword=keyword)


if __name__ == "__main__":
    app.run(debug=True)
