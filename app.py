# JWT
import os  # .env에서 JWT 비밀키 read

from dotenv import load_dotenv  # .env파일 읽기
from flask import Flask

from routes import register_blueprints

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "FLASK_SECRET_KEY", "development-only-flask-secret"
)

# JWT 관련 설정은 실제 Flask 앱에서 관리
app.config["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", "development-only-secret-change-before-deploy"
)
app.config["JWT_EXPIRES_MINUTES"] = 60
app.config["JWT_COOKIE_SECURE"] = (
    os.environ.get("JWT_COOKIE_SECURE", "false").lower() == "true"  # .env의 문자열을 bool값으로 변환
)

register_blueprints(app)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
