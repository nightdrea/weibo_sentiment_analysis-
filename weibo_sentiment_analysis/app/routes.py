from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db, limiter, cache
from app.models import User, WeiboPost, WeiboComment
from app.crawlers.weibo_crawler import WeiboCrawler
from werkzeug.security import generate_password_hash, check_password_hash

@app.route("/")
@app.route("/home")
@login_required
def home():
    # 从数据库获取最近的微博数据（已分页）
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 缓存暂时禁用，避免序列化错误
    recent_posts = WeiboPost.query.order_by(WeiboPost.publish_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
    total_posts = WeiboPost.query.count()
    total_comments = WeiboComment.query.count()
    
    # 计算统计数据
    stats = {
        'total_posts': total_posts,
        'total_comments': total_comments,
        'recent_posts': recent_posts
    }
    
    return render_template('index.html', current_user=current_user, stats=stats, page=page, per_page=per_page)

@app.route("/register", methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # 检查用户名是否已存在
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template('register.html', error='用户名已存在')
        
        # 检查邮箱是否已存在
        user = User.query.filter_by(email=email).first()
        if user:
            return render_template('register.html', error='邮箱已被注册')
        
        # 创建新用户
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            return render_template('login.html', error='用户名或密码错误')
        
        login_user(user)
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/sentiment")
@login_required
def sentiment():
    # 缓存暂时禁用，避免序列化错误
    # 从数据库获取情感分析数据
    total_posts = WeiboPost.query.count()
    total_comments = WeiboComment.query.count()
    
    return render_template('sentiment.html', current_user=current_user, total_posts=total_posts, total_comments=total_comments)

@app.route("/visualization")
@login_required
def visualization():
    # 缓存暂时禁用，避免序列化错误
    # 从数据库获取可视化数据
    posts = WeiboPost.query.order_by(WeiboPost.publish_time.desc()).limit(20).all()
    
    return render_template('visualization.html', current_user=current_user, posts=posts)

@app.route("/article")
@login_required
def article():
    # 从数据库获取文章分析数据（已分页）
    page = request.args.get('page', 1, type=int)
    per_page = 20
    posts = WeiboPost.query.order_by(WeiboPost.publish_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
    total_posts = WeiboPost.query.count()
    return render_template('article.html', current_user=current_user, total_posts=total_posts, posts=posts, page=page, per_page=per_page)

@app.route("/ip")
@login_required
def ip():
    # 从数据库获取IP分析数据（已分页）
    page = request.args.get('page', 1, type=int)
    per_page = 20
    posts = WeiboPost.query.filter(WeiboPost.ip_location.isnot(None)).order_by(WeiboPost.publish_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
    comments = WeiboComment.query.filter(WeiboComment.ip_location.isnot(None)).order_by(WeiboComment.comment_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('ip.html', current_user=current_user, posts=posts, comments=comments, page=page, per_page=per_page)

@app.route("/comment")
@login_required
def comment():
    # 从数据库获取评论分析数据（已分页）
    page = request.args.get('page', 1, type=int)
    per_page = 20
    comments = WeiboComment.query.order_by(WeiboComment.comment_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
    total_comments = WeiboComment.query.count()
    return render_template('comment.html', current_user=current_user, total_comments=total_comments, comments=comments, page=page, per_page=per_page)

@app.route("/public-opinion")
@login_required
def public_opinion():
    # 从数据库获取舆情分析数据（已分页）
    page = request.args.get('page', 1, type=int)
    per_page = 20
    posts = WeiboPost.query.order_by(WeiboPost.publish_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('public_opinion.html', current_user=current_user, posts=posts, page=page, per_page=per_page)

@app.route("/wordcloud")
@login_required
def wordcloud():
    # 从数据库获取词云数据
    posts = WeiboPost.query.all()
    comments = WeiboComment.query.all()
    return render_template('wordcloud.html', current_user=current_user, posts=posts, comments=comments)

@app.route("/content-wordcloud")
@login_required
def content_wordcloud():
    # 从数据库获取内容词云数据
    posts = WeiboPost.query.all()
    return render_template('content_wordcloud.html', current_user=current_user, posts=posts)

@app.route("/comment-wordcloud")
@login_required
def comment_wordcloud():
    # 从数据库获取评论词云数据
    comments = WeiboComment.query.all()
    return render_template('comment_wordcloud.html', current_user=current_user, comments=comments)

@app.route("/user-wordcloud")
@login_required
def user_wordcloud():
    # 从数据库获取用户词云数据
    comments = WeiboComment.query.all()
    return render_template('user_wordcloud.html', current_user=current_user, comments=comments)

@app.route("/crawl", methods=['GET', 'POST'])
@login_required
def crawl():
    # 默认使用 MediaCrawler
    crawler = WeiboCrawler(use_media_crawler=True)
    hot_topics = crawler.crawl_hot_topics()
    
    if request.method == 'POST':
        keyword = request.form.get('keyword')
        pages = int(request.form.get('pages', 1))
        crawl_comments = request.form.get('crawl_comments') == 'on'
        
        try:
            # 开始爬取帖子
            posts = crawler.crawl_posts(keyword, pages)
            
            # 如果需要爬取评论
            if crawl_comments and posts:
                for post in posts:
                    crawler.crawl_comments(post.id, pages=2)
            
            result = {
                'success': True,
                'message': f'成功爬取 {len(posts)} 条微博帖子'
            }
        except Exception as e:
            result = {
                'success': False,
                'message': f'爬取失败: {str(e)}'
            }
        
        return render_template('crawl.html', current_user=current_user, result=result, hot_topics=hot_topics)
    
    return render_template('crawl.html', current_user=current_user, hot_topics=hot_topics)

@app.route("/search", methods=['GET', 'POST'])
@login_required
def search():
    # 搜索功能
    if request.method == 'POST':
        keyword = request.form.get('keyword')
        search_type = request.form.get('search_type', 'all')
        
        # 构建查询
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        if search_type == 'posts':
            # 搜索微博帖子
            posts = WeiboPost.query.filter(
                WeiboPost.content.contains(keyword)
            ).order_by(WeiboPost.publish_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
            comments = []
        elif search_type == 'comments':
            # 搜索评论
            comments = WeiboComment.query.filter(
                WeiboComment.content.contains(keyword)
            ).order_by(WeiboComment.comment_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
            posts = []
        else:
            # 搜索所有
            posts = WeiboPost.query.filter(
                WeiboPost.content.contains(keyword)
            ).order_by(WeiboPost.publish_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
            comments = WeiboComment.query.filter(
                WeiboComment.content.contains(keyword)
            ).order_by(WeiboComment.comment_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
        
        return render_template('search.html', current_user=current_user, keyword=keyword, search_type=search_type, posts=posts, comments=comments, page=page, per_page=per_page)
    
    return render_template('search.html', current_user=current_user)

@app.route("/export", methods=['GET', 'POST'])
@login_required
def export():
    # 数据导出功能
    if request.method == 'POST':
        export_type = request.form.get('export_type')
        data_type = request.form.get('data_type')
        
        import csv
        import json
        from io import StringIO
        from flask import send_file
        
        if data_type == 'posts':
            # 导出微博帖子
            posts = WeiboPost.query.all()
            
            if export_type == 'csv':
                # 导出为 CSV
                output = StringIO()
                writer = csv.writer(output)
                writer.writerow(['ID', '作者', '内容', '发布时间', '点赞数', '评论数', '转发数', 'IP位置'])
                for post in posts:
                    writer.writerow([
                        post.id,
                        post.author,
                        post.content,
                        post.publish_time.strftime('%Y-%m-%d %H:%M:%S'),
                        post.likes,
                        post.comments_count,
                        post.reposts,
                        post.ip_location or ''
                    ])
                output.seek(0)
                return send_file(
                    output,
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name='weibo_posts.csv'
                )
            elif export_type == 'json':
                # 导出为 JSON
                data = []
                for post in posts:
                    data.append({
                        'id': post.id,
                        'author': post.author,
                        'content': post.content,
                        'publish_time': post.publish_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'likes': post.likes,
                        'comments_count': post.comments_count,
                        'reposts': post.reposts,
                        'ip_location': post.ip_location or ''
                    })
                output = StringIO()
                json.dump(data, output, ensure_ascii=False, indent=2)
                output.seek(0)
                return send_file(
                    output,
                    mimetype='application/json',
                    as_attachment=True,
                    download_name='weibo_posts.json'
                )
        elif data_type == 'comments':
            # 导出评论
            comments = WeiboComment.query.all()
            
            if export_type == 'csv':
                # 导出为 CSV
                output = StringIO()
                writer = csv.writer(output)
                writer.writerow(['ID', '帖子ID', '评论者', '内容', '评论时间', '点赞数', 'IP位置'])
                for comment in comments:
                    writer.writerow([
                        comment.id,
                        comment.post_id,
                        comment.commenter,
                        comment.content,
                        comment.comment_time.strftime('%Y-%m-%d %H:%M:%S'),
                        comment.likes,
                        comment.ip_location or ''
                    ])
                output.seek(0)
                return send_file(
                    output,
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name='weibo_comments.csv'
                )
            elif export_type == 'json':
                # 导出为 JSON
                data = []
                for comment in comments:
                    data.append({
                        'id': comment.id,
                        'post_id': comment.post_id,
                        'commenter': comment.commenter,
                        'content': comment.content,
                        'comment_time': comment.comment_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'likes': comment.likes,
                        'ip_location': comment.ip_location or ''
                    })
                output = StringIO()
                json.dump(data, output, ensure_ascii=False, indent=2)
                output.seek(0)
                return send_file(
                    output,
                    mimetype='application/json',
                    as_attachment=True,
                    download_name='weibo_comments.json'
                )
    
    return render_template('export.html', current_user=current_user)
