from app import app, db
from app.models import User, WeiboPost, WeiboComment

with app.app_context():
    # 创建所有表
    db.create_all()
    print('数据库表创建完成！')
