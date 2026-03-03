import requests
import time
import random
from datetime import datetime
from app import db
from app.models import WeiboPost, WeiboComment
from bs4 import BeautifulSoup
from app.crawlers.media_crawler_adapter import MediaCrawlerAdapter

class WeiboCrawler:
    def __init__(self, use_media_crawler=False, media_crawler_path=None):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive'
        }
        self.proxies = None  # 可以设置代理IP
        self.use_media_crawler = use_media_crawler
        self.media_crawler_adapter = MediaCrawlerAdapter(media_crawler_path) if use_media_crawler else None
        print(f"WeiboCrawler 初始化: use_media_crawler={use_media_crawler}")
    
    def crawl_posts(self, keyword, pages=5):
        """爬取指定关键词的微博帖子"""
        # 如果启用了 MediaCrawler，使用适配器爬取
        if self.use_media_crawler and self.media_crawler_adapter:
            print(f"使用 MediaCrawler 爬取关键词: {keyword}, 页数: {pages}")
            return self.media_crawler_adapter.crawl_weibo(keyword, pages)
        
        # 否则使用传统方法爬取
        posts = []
        for page in range(1, pages + 1):
            try:
                # 构建请求URL（这里使用微博搜索API的模拟，实际需要根据微博的API进行调整）
                url = f'https://s.weibo.com/weibo?q={keyword}&page={page}'
                print(f"正在爬取第 {page} 页: {url}")
                response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=10)
                
                if response.status_code == 200:
                    print(f"成功获取页面，状态码: {response.status_code}")
                    print(f"页面长度: {len(response.text)} 字符")
                    
                    # 保存页面内容到文件，方便调试
                    with open(f'weibo_page_{page}.html', 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    print(f"页面内容已保存到 weibo_page_{page}.html")
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # 打印页面标题，确认是否成功获取
                    title = soup.title.get_text() if soup.title else '无标题'
                    print(f"页面标题: {title}")
                    
                    # 尝试不同的选择器来查找微博帖子
                    post_elements = soup.select('.card-wrap')
                    print(f"找到 {len(post_elements)} 个帖子元素")
                    
                    # 如果没找到，尝试其他选择器
                    if len(post_elements) == 0:
                        post_elements = soup.select('.card')
                        print(f"尝试其他选择器，找到 {len(post_elements)} 个帖子元素")
                    
                    # 尝试微博搜索结果的选择器
                    if len(post_elements) == 0:
                        post_elements = soup.select('.pl_cont')
                        print(f"尝试微博搜索结果选择器，找到 {len(post_elements)} 个帖子元素")
                    
                    # 尝试微博主页的选择器
                    if len(post_elements) == 0:
                        post_elements = soup.select('.WB_cardwrap')
                        print(f"尝试微博主页选择器，找到 {len(post_elements)} 个帖子元素")
                    
                    for post in post_elements:
                        try:
                            # 提取帖子信息
                            # 尝试不同的选择器来提取内容
                            content = ''
                            if post.select_one('.txt'):
                                content = post.select_one('.txt').get_text(strip=True)
                            elif post.select_one('.WB_text'):
                                content = post.select_one('.WB_text').get_text(strip=True)
                            elif post.select_one('.content'):
                                content = post.select_one('.content').get_text(strip=True)
                            
                            # 尝试不同的选择器来提取作者
                            author = ''
                            if post.select_one('.info .name'):
                                author = post.select_one('.info .name').get_text(strip=True)
                            elif post.select_one('.WB_info .WB_name'):
                                author = post.select_one('.WB_info .WB_name').get_text(strip=True)
                            elif post.select_one('.user_name'):
                                author = post.select_one('.user_name').get_text(strip=True)
                            
                            # 尝试不同的选择器来提取发布时间
                            publish_time = ''
                            if post.select_one('.from'):
                                publish_time = post.select_one('.from').get_text(strip=True)
                            elif post.select_one('.WB_from'):
                                publish_time = post.select_one('.WB_from').get_text(strip=True)
                            elif post.select_one('.time'):
                                publish_time = post.select_one('.time').get_text(strip=True)
                            
                            # 尝试不同的选择器来提取点赞数
                            likes = 0
                            if post.select_one('.like'):
                                like_text = post.select_one('.like').get_text(strip=True)
                                if like_text.isdigit():
                                    likes = int(like_text)
                            elif post.select_one('.WB_feed_handle .like'):
                                like_text = post.select_one('.WB_feed_handle .like').get_text(strip=True)
                                if like_text.isdigit():
                                    likes = int(like_text)
                            
                            # 尝试不同的选择器来提取评论数
                            comments_count = 0
                            if post.select_one('.comment'):
                                comment_text = post.select_one('.comment').get_text(strip=True)
                                if comment_text.isdigit():
                                    comments_count = int(comment_text)
                            elif post.select_one('.WB_feed_handle .comment'):
                                comment_text = post.select_one('.WB_feed_handle .comment').get_text(strip=True)
                                if comment_text.isdigit():
                                    comments_count = int(comment_text)
                            
                            # 尝试不同的选择器来提取转发数
                            reposts = 0
                            if post.select_one('.repost'):
                                repost_text = post.select_one('.repost').get_text(strip=True)
                                if repost_text.isdigit():
                                    reposts = int(repost_text)
                            elif post.select_one('.WB_feed_handle .repost'):
                                repost_text = post.select_one('.WB_feed_handle .repost').get_text(strip=True)
                                if repost_text.isdigit():
                                    reposts = int(repost_text)
                            
                            # 尝试不同的选择器来提取IP位置
                            ip_location = ''
                            if post.select_one('.from a'):
                                ip_location = post.select_one('.from a').get_text(strip=True)
                            elif post.select_one('.WB_from a'):
                                ip_location = post.select_one('.WB_from a').get_text(strip=True)
                            elif post.select_one('.ip'):
                                ip_location = post.select_one('.ip').get_text(strip=True)
                            
                            # 打印提取的信息
                            print(f"\n提取的帖子信息:")
                            print(f"作者: {author}")
                            print(f"内容: {content[:100]}...")
                            print(f"发布时间: {publish_time}")
                            print(f"点赞: {likes}")
                            print(f"评论: {comments_count}")
                            print(f"转发: {reposts}")
                            print(f"IP位置: {ip_location}")
                            
                            # 解析发布时间
                            try:
                                publish_time = datetime.strptime(publish_time, '%Y-%m-%d %H:%M')
                            except:
                                publish_time = datetime.now()
                            
                            # 存储到数据库
                            new_post = WeiboPost(
                                content=content,
                                author=author,
                                publish_time=publish_time,
                                likes=likes,
                                comments_count=comments_count,
                                reposts=reposts,
                                ip_location=ip_location
                            )
                            db.session.add(new_post)
                            posts.append(new_post)
                            
                        except Exception as e:
                            print(f"解析帖子失败: {e}")
                    
                    # 随机延迟，避免被封
                    time.sleep(random.uniform(1, 3))
                else:
                    print(f"请求失败，状态码: {response.status_code}")
                    time.sleep(5)
            except Exception as e:
                print(f"爬取页面 {page} 失败: {e}")
                time.sleep(5)
        
        # 批量提交到数据库
        if posts:
            try:
                db.session.commit()
                print(f"成功爬取并存储 {len(posts)} 条微博帖子")
            except Exception as e:
                print(f"存储帖子失败: {e}")
                db.session.rollback()
        
        return posts
    
    def crawl_comments(self, post_id, pages=3):
        """爬取指定微博帖子的评论"""
        comments = []
        for page in range(1, pages + 1):
            try:
                # 构建评论请求URL（这里需要根据实际的微博评论API进行调整）
                url = f'https://weibo.com/ajax/statuses/comments?mid={post_id}&page={page}'
                response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    # 解析评论数据
                    comment_list = data.get('data', {}).get('comments', [])
                    
                    for comment in comment_list:
                        try:
                            # 提取评论信息
                            content = comment.get('text', '')
                            commenter = comment.get('user', {}).get('screen_name', '')
                            comment_time = comment.get('created_at', '')
                            likes = comment.get('like_counts', 0)
                            ip_location = comment.get('source', '')
                            
                            # 解析评论时间
                            try:
                                comment_time = datetime.strptime(comment_time, '%a %b %d %H:%M:%S %z %Y')
                            except:
                                comment_time = datetime.now()
                            
                            # 存储到数据库
                            new_comment = WeiboComment(
                                post_id=post_id,
                                content=content,
                                commenter=commenter,
                                comment_time=comment_time,
                                likes=likes,
                                ip_location=ip_location
                            )
                            db.session.add(new_comment)
                            comments.append(new_comment)
                            
                        except Exception as e:
                            print(f"解析评论失败: {e}")
                    
                    # 随机延迟
                    time.sleep(random.uniform(1, 2))
                else:
                    print(f"请求评论失败，状态码: {response.status_code}")
                    time.sleep(3)
            except Exception as e:
                print(f"爬取评论页面 {page} 失败: {e}")
                time.sleep(3)
        
        # 批量提交到数据库
        if comments:
            try:
                db.session.commit()
                print(f"成功爬取并存储 {len(comments)} 条评论")
            except Exception as e:
                print(f"存储评论失败: {e}")
                db.session.rollback()
        
        return comments
    
    def crawl_hot_topics(self):
        """爬取微博热搜话题"""
        # 如果启用了 MediaCrawler，使用适配器爬取
        if self.use_media_crawler and self.media_crawler_adapter:
            print("使用 MediaCrawler 爬取微博热搜")
            return self.media_crawler_adapter.crawl_hot_topics()
        
        # 否则使用传统方法爬取
        try:
            url = 'https://s.weibo.com/top/summary'
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # 解析热搜话题
                hot_topics = []
                topic_elements = soup.select('.td-02')
                
                for topic in topic_elements:
                    try:
                        title = topic.select_one('a').get_text(strip=True) if topic.select_one('a') else ''
                        heat = topic.select_one('.txt').get_text(strip=True) if topic.select_one('.txt') else ''
                        hot_topics.append({'title': title, 'heat': heat})
                    except Exception as e:
                        print(f"解析热搜话题失败: {e}")
                
                print(f"成功爬取 {len(hot_topics)} 个热搜话题")
                return hot_topics
            else:
                print(f"请求热搜失败，状态码: {response.status_code}")
                return []
        except Exception as e:
            print(f"爬取热搜失败: {e}")
            return []
