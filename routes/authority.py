# JWT
from datetime import datetime, timedelta, timezone  # JWT의 발급시각, 만료시각
from functools import wraps

import jwt  # PyJWT
from flask import (
    Blueprint,
    current_app,
    g,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from pymongo.errors import DuplicateKeyError
from werkzeug.security import check_password_hash, generate_password_hash

from db import ensure_database_indexes, get_users_collection


# 인증 관련 라우트를 담는 Blueprint
auth_bp = Blueprint("auth", __name__)


def load_user_id():
    # id 찾는 함수: 기본값은 비로그인 상태
    g.user_id = None

    # 쿠키에서 JWT 문자열을 가져옴
    token = request.cookies.get("access_token")
    if not token:
        return  # 아무것도 없으면 route함수 실행

    # JWT 디코딩해서 id찾기
    try:
        g.user_id = jwt.decode(
            token,
            current_app.config["JWT_SECRET_KEY"],
            algorithms=["HS256"],
        )["sub"]
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError):
        g.user_id = None


@auth_bp.before_app_request
def set_current_user():
    # HTTP요청이 왔을 때 모든 Blueprint의 route함수보다 먼저 실행
    load_user_id()


@auth_bp.app_context_processor
def inject_current_user():
    # render_template()로 HTML을 렌더링할 때 모든 HTML에 공통변수 전달
    return {"load_user_id": getattr(g, "user_id", None)}


def login_required(view):
    # 로그인 검증 함수, 비로그인시 로그인 화면으로
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        # 쿠키에서 JWT 문자열을 가져옴
        token = request.cookies.get("access_token")
        if not token:  # JWT가 없으면 로그인하지 않음
            return redirect(url_for("auth.login", next=request.full_path))

        try:
            # JWT 디코딩, g는 flask가 제공하는 임시 저장 공간
            g.user_id = jwt.decode(
                token,
                current_app.config["JWT_SECRET_KEY"],
                algorithms=["HS256"],
            )["sub"]
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError):
            # exp 만료, JWT 형식 오류, sub값이 없는 경우
            response = make_response(
                redirect(url_for("auth.login", next=request.full_path))
            )
            response.delete_cookie("access_token")  # 쿠키 삭제
            response.headers["Cache-Control"] = "no-store" # 뒤로가기
            return response

        return view(*args, **kwargs)

    return wrapped_view


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", registered=request.args.get("registered"))

    # id 또는 비밀번호가 없는 경우
    user_id_receive = request.form.get("id_give", "").strip()
    password_receive = request.form.get("password_give", "")
    if not user_id_receive or not password_receive:
        return render_template("login.html", error="아이디와 비밀번호를 입력해주세요."), 400

    # id가 없거나 비밀번호가 틀린경우
    user = get_users_collection().find_one({"user_id": user_id_receive})
    if not user or not check_password_hash(user["password_hash"], password_receive):
        return render_template("login.html", error="아이디 또는 비밀번호가 올바르지 않습니다."), 401

    # jwt 생성
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "sub": user_id_receive,
            "iat": now,
            "exp": now + timedelta(minutes=current_app.config["JWT_EXPIRES_MINUTES"]),
        },
        current_app.config["JWT_SECRET_KEY"],
        algorithm="HS256",
    )

    # 로그인 성공 후 쿠키 발급
    response = make_response(redirect(url_for("main.index")))   # 브라우저에 보낼 응답 객체, 메인페이지로 보내는 정보
    response.set_cookie(
        "access_token",
        token,
        max_age=current_app.config["JWT_EXPIRES_MINUTES"] * 60,  # 브라우저 쿠키 유지 시간
        httponly=True,  # 브라우저의 JS가 쿠키를 직접 읽기 어렵게 해 XSS공격 방어
        secure=current_app.config["JWT_COOKIE_SECURE"], # JWT_COOKIE_SECURE = True 인 경우 쿠키를 HTTPS 요청에만 같이 보냄
        samesite="Lax",  # 외부 사이트에서 쿠키 요청시 POST 전송 제한
    )
    return response


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    # id, pw받기
    user_id = request.form.get("id_give", "").strip()
    password = request.form.get("password_give", "")
    if not user_id or not password:
        return render_template("signup.html", error="아이디와 비밀번호를 입력해주세요."), 400   # 형식이 올바르지 않음

    # DB에 넣을 데이터
    user = {
        "user_id": user_id,
        "password_hash": generate_password_hash(password),
    }

    # 중복 검증
    try:
        ensure_database_indexes()
        get_users_collection().insert_one(user)
    except DuplicateKeyError:
        return render_template("signup.html", error="이미 사용 중인 ID입니다."), 409        # 현재 데이터와 충돌

    return redirect(url_for("auth.login", registered="1"))


@auth_bp.route("/logout", methods=["POST"])
def logout():
    response = make_response(redirect(url_for("auth.login")))
    response.delete_cookie("access_token")
    return response
