# JWT
import os  # .env에서 JWT 비밀키 read

from dotenv import load_dotenv  # .env파일 읽기
from flask import Flask

from routes.authority import auth_bp
from routes.main import main_bp
from routes.mypage import mypage_bp

load_dotenv()

app = Flask(__name__)

# JWT 관련 설정은 실제 Flask 앱에서 관리
app.config["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", "development-only-secret-change-before-deploy"
)
app.config["JWT_EXPIRES_MINUTES"] = 60
app.config["JWT_COOKIE_SECURE"] = (
    os.environ.get("JWT_COOKIE_SECURE", "false").lower() == "true"
)

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(mypage_bp)

if __name__ == "__main__":
    app.run(debug=True)
