import subprocess
import json
import os
from datetime import datetime
from app import app, db
from app.models import WeiboPost, WeiboComment

class MediaCrawlerAdapter:
    def __init__(self, media_crawler_path=None):
        """初始化 MediaCrawler 适配器
        
        Args:
            media_crawler_path: MediaCrawler 项目的路径，如果为 None 则使用默认路径
        """
        if media_crawler_path:
            self.media_crawler_path = media_crawler_path
        else:
            # 默认路径，直接指定为 E:\舆情分析系统\2\MediaCrawler
            self.media_crawler_path = r"E:\舆情分析系统\2\MediaCrawler"
        
        # 规范化路径
        self.media_crawler_path = os.path.normpath(self.media_crawler_path)
        print(f"MediaCrawler 路径: {self.media_crawler_path}")
    
    def crawl_weibo(self, keyword, pages=5):
        """使用 MediaCrawler 爬取微博
        
        Args:
            keyword: 搜索关键词
            pages: 爬取页数
            
        Returns:
            爬取的微博帖子列表
        """
        try:
            # 构建命令（使用 Python 执行）
            cmd = [
                "python", "main.py",
                "--platform", "wb",
                "--keywords", keyword,
                "--start", "1",
                "--end", str(pages),
                "--save_data_option", "json",
                "--lt", "cookie",
                "--headless", "true",
                "--thread", "5",  # 启用多线程爬取，提高速度
                "--interval", "1"  # 减少请求间隔，提高速度
            ]
            
            print(f"执行命令: {' '.join(cmd)}")
            print(f"工作目录: {self.media_crawler_path}")
            
            # 执行命令
            result = subprocess.run(
                cmd,
                cwd=self.media_crawler_path,
                capture_output=True,
                text=False,  # 以字节形式获取输出，避免编码问题
                timeout=300  # 5分钟超时
            )
            
            print(f"命令执行状态码: {result.returncode}")
            
            # 尝试解码输出
            stdout = ""
            try:
                stdout = result.stdout.decode('utf-8', errors='replace')
                print(f"标准输出长度: {len(stdout)} 字符")
                print(f"标准输出前 1000 字符: {stdout[:1000]}...")
            except Exception as e:
                print(f"解码输出失败: {e}")
            
            # 尝试解码错误输出
            stderr = ""
            try:
                stderr = result.stderr.decode('utf-8', errors='replace')
                print(f"标准错误长度: {len(stderr)} 字符")
                print(f"标准错误前 1000 字符: {stderr[:1000]}...")
            except Exception as e:
                print(f"解码错误输出失败: {e}")
            
            if result.returncode != 0:
                print(f"MediaCrawler 执行失败: {stderr}")
                return []
            
            # 检查输出是否包含 JSON 数据
            if not stdout:
                print("输出为空，检查是否有输出文件")
                
                # 检查 MediaCrawler 的数据保存目录
                data_dir = os.path.join(self.media_crawler_path, "data")
                if os.path.exists(data_dir):
                    print(f"数据目录存在: {data_dir}")
                    # 查找最新的 JSON 文件
                    json_files = []
                    for root, dirs, files in os.walk(data_dir):
                        for file in files:
                            if file.endswith('.json'):
                                json_files.append(os.path.join(root, file))
                    
                    if json_files:
                        # 按修改时间排序，取最新的
                        json_files.sort(key=os.path.getmtime, reverse=True)
                        latest_json_file = json_files[0]
                        print(f"找到最新的 JSON 文件: {latest_json_file}")
                        
                        # 读取文件内容
                        try:
                            with open(latest_json_file, 'r', encoding='utf-8', errors='replace') as f:
                                stdout = f.read()
                            print(f"从文件中读取到 {len(stdout)} 字符")
                        except Exception as e:
                            print(f"读取 JSON 文件失败: {e}")
                            return []
                    else:
                        print("没有找到 JSON 文件")
                        return []
                else:
                    print("数据目录不存在")
                    return []
            
            # 尝试解析输出
            try:
                # 尝试直接解析
                data = json.loads(stdout)
                print("成功解析 JSON 数据")
            except json.JSONDecodeError as e:
                print(f"直接解析 JSON 失败: {e}")
                
                # 尝试从输出中提取 JSON 部分
                try:
                    # 查找 JSON 开始和结束位置
                    start = stdout.find('[{')
                    end = stdout.rfind('}]') + 2
                    print(f"JSON 开始位置: {start}, 结束位置: {end}")
                    
                    if start != -1 and end != -1:
                        json_str = stdout[start:end]
                        print(f"提取的 JSON 字符串长度: {len(json_str)}")
                        print(f"提取的 JSON 字符串前 500 字符: {json_str[:500]}...")
                        data = json.loads(json_str)
                        print("成功从输出中提取并解析 JSON 部分")
                    else:
                        # 尝试查找其他 JSON 格式
                        start = stdout.find('{')
                        end = stdout.rfind('}') + 1
                        print(f"尝试其他 JSON 格式，开始位置: {start}, 结束位置: {end}")
                        
                        if start != -1 and end != -1:
                            json_str = stdout[start:end]
                            print(f"提取的 JSON 字符串长度: {len(json_str)}")
                            print(f"提取的 JSON 字符串前 500 字符: {json_str[:500]}...")
                            data = json.loads(json_str)
                            print("成功从输出中提取并解析 JSON 部分")
                        else:
                            print("无法找到 JSON 数据")
                            return []
                except Exception as e2:
                    print(f"提取 JSON 部分失败: {e2}")
                    return []
            
            # 转换为系统数据模型
            posts = []
            with app.app_context():
                for item in data:
                    try:
                        # 提取帖子信息
                        content = item.get('content', '')
                        author = item.get('author', '')
                        publish_time_str = item.get('publish_time', '')
                        likes = int(item.get('likes', 0))
                        comments_count = int(item.get('comments', 0))
                        reposts = int(item.get('reposts', 0))
                        ip_location = item.get('ip_location', '')
                        
                        # 解析发布时间
                        try:
                            # 尝试不同的时间格式
                            publish_time = datetime.strptime(publish_time_str, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            try:
                                publish_time = datetime.strptime(publish_time_str, '%Y-%m-%d')
                            except ValueError:
                                publish_time = datetime.now()
                        
                        # 创建 WeiboPost 对象
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
                        
                        # 处理评论
                        comment_items = item.get('comments', [])
                        for comment_item in comment_items:
                            try:
                                comment_content = comment_item.get('content', '')
                                commenter = comment_item.get('commenter', '')
                                comment_time_str = comment_item.get('comment_time', '')
                                comment_likes = int(comment_item.get('likes', 0))
                                
                                # 解析评论时间
                                try:
                                    comment_time = datetime.strptime(comment_time_str, '%Y-%m-%d %H:%M:%S')
                                except ValueError:
                                    comment_time = datetime.now()
                                
                                # 创建 WeiboComment 对象
                                new_comment = WeiboComment(
                                    post_id=new_post.id,
                                    content=comment_content,
                                    commenter=commenter,
                                    comment_time=comment_time,
                                    likes=comment_likes,
                                    ip_location=comment_item.get('ip_location', '')
                                )
                                db.session.add(new_comment)
                            except Exception as e:
                                print(f"处理评论失败: {e}")
                                continue
                        
                    except Exception as e:
                        print(f"处理帖子失败: {e}")
                        continue
                
                # 提交到数据库
                if posts:
                    try:
                        db.session.commit()
                        print(f"成功存储 {len(posts)} 条帖子及相关评论")
                    except Exception as e:
                        print(f"存储数据失败: {e}")
                        db.session.rollback()
                        posts = []
            
            return posts
            
        except Exception as e:
            print(f"使用 MediaCrawler 爬取失败: {e}")
            return []
    
    def crawl_hot_topics(self):
        """使用 MediaCrawler 爬取微博热搜
        
        Returns:
            热搜话题列表
        """
        try:
            # 构建命令
            cmd = [
                "python", "main.py",
                "--platform", "wb",
                "--type", "search",
                "--keywords", "热搜",
                "--save_data_option", "json"
            ]
            
            print(f"执行命令: {' '.join(cmd)}")
            
            # 执行命令
            result = subprocess.run(
                cmd,
                cwd=self.media_crawler_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            print(f"命令执行状态码: {result.returncode}")
            print(f"标准输出: {result.stdout[:500]}...")
            print(f"标准错误: {result.stderr[:500]}...")
            
            if result.returncode != 0:
                print(f"MediaCrawler 执行失败: {result.stderr}")
                return []
            
            # 解析输出
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                print(f"解析 JSON 失败: {e}")
                return []
            
            # 转换为标准格式
            hot_topics = []
            for item in data:
                try:
                    title = item.get('title', '')
                    heat = item.get('heat', '')
                    hot_topics.append({'title': title, 'heat': heat})
                except Exception as e:
                    print(f"处理热搜话题失败: {e}")
                    continue
            
            print(f"成功爬取 {len(hot_topics)} 个热搜话题")
            return hot_topics
            
        except Exception as e:
            print(f"爬取热搜失败: {e}")
            return []