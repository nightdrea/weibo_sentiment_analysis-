from app import app, db
from app.models import WeiboPost, WeiboComment
from datetime import datetime, timedelta
import random

# 创建测试数据
def add_test_data():
    print("开始添加测试数据...")
    
    # 设置应用上下文
    with app.app_context():
        # 创建测试微博帖子
        keywords = ["人工智能", "机器学习", "深度学习", "自然语言处理", "计算机视觉"]
        authors = ["科技达人", "AI研究者", "数据科学家", "程序员小王", "技术爱好者"]
        locations = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "西安"]
        
        posts = []
        for i in range(50):
            keyword = random.choice(keywords)
            content = f"今天学习了{keyword}的相关知识，感觉非常有趣！#科技 #AI {keyword}"
            author = random.choice(authors)
            publish_time = datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            likes = random.randint(0, 1000)
            comments_count = random.randint(0, 200)
            reposts = random.randint(0, 500)
            ip_location = random.choice(locations)
            
            post = WeiboPost(
                content=content,
                author=author,
                publish_time=publish_time,
                likes=likes,
                comments_count=comments_count,
                reposts=reposts,
                ip_location=ip_location
            )
            posts.append(post)
        
        # 批量添加帖子
        db.session.add_all(posts)
        try:
            db.session.commit()
            print(f"成功添加 {len(posts)} 条测试微博帖子")
        except Exception as e:
            print(f"添加帖子失败: {e}")
            db.session.rollback()
            return
        
        # 创建测试评论
        comments = []
        commenters = ["热心网友", "技术粉丝", "AI爱好者", "路人甲", "专业人士"]
        comment_contents = [
            "非常赞同你的观点！",
            "学习了，谢谢分享！",
            "请问有相关的学习资料推荐吗？",
            "这个技术前景很好",
            "我也在研究这个方向",
            "说得很有道理",
            "期待更多分享",
            "点赞支持！",
            "受益匪浅",
            "希望能详细解释一下"
        ]
        
        # 获取所有帖子
        all_posts = WeiboPost.query.all()
        for post in all_posts:
            # 为每个帖子添加一些评论
            num_comments = random.randint(0, 10)
            for _ in range(num_comments):
                comment_content = random.choice(comment_contents)
                commenter = random.choice(commenters)
                comment_time = post.publish_time + timedelta(hours=random.randint(0, 48))
                likes = random.randint(0, 50)
                ip_location = random.choice(locations)
                
                comment = WeiboComment(
                    post_id=post.id,
                    content=comment_content,
                    commenter=commenter,
                    comment_time=comment_time,
                    likes=likes,
                    ip_location=ip_location
                )
                comments.append(comment)
        
        # 批量添加评论
        if comments:
            db.session.add_all(comments)
            try:
                db.session.commit()
                print(f"成功添加 {len(comments)} 条测试评论")
            except Exception as e:
                print(f"添加评论失败: {e}")
                db.session.rollback()
        
        print("测试数据添加完成！")

if __name__ == "__main__":
    add_test_data()