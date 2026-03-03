from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import os

# 获取当前文件的目录路径
base_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录路径
project_dir = os.path.dirname(base_dir)
# 模板文件夹路径
templates_dir = os.path.join(project_dir, 'templates')

app = Flask(__name__, template_folder=templates_dir)
# 生成更复杂的 SECRET_KEY
app.config['SECRET_KEY'] = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weibo_sentiment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化 CSRF 保护
csrf = CSRFProtect(app)

# 初始化速率限制
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# 初始化缓存
cache = Cache(app, config={
    'CACHE_TYPE': 'simple',  # 使用内存缓存
    'CACHE_DEFAULT_TIMEOUT': 300  # 默认缓存5分钟
})

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from app import routes, models

# 启动定时任务的函数
def start_tasks():
    from app import tasks
    tasks.start_scheduled_tasks()
