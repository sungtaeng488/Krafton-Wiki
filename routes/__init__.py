"""Application route blueprints."""
from .main import main_bp
from .write import write_bp
from .search import search_bp
from .post import post_bp
from .authority import auth_bp
from .mypage import mypage_bp

all_blueprints = [
    main_bp, 
    write_bp, 
    search_bp, 
    post_bp,
    auth_bp,
    mypage_bp,
]
