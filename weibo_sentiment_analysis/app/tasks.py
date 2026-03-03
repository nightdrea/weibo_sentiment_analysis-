import schedule
import time
import threading
from app.crawlers.weibo_crawler import WeiboCrawler

# 初始化爬虫
crawler = WeiboCrawler(use_media_crawler=True)

# 定时爬取任务
def crawl_task():
    """定时爬取微博热搜和热门话题"""
    print("开始执行定时爬取任务...")
    try:
        # 爬取微博热搜
        hot_topics = crawler.crawl_hot_topics()
        print(f"成功爬取 {len(hot_topics)} 个热搜话题")
        
        # 对前5个热搜话题进行深度爬取
        for i, topic in enumerate(hot_topics[:5]):
            keyword = topic.get('title', '')
            if keyword:
                print(f"爬取热搜话题: {keyword}")
                posts = crawler.crawl_posts(keyword, pages=2)
                print(f"成功爬取 {len(posts)} 条微博帖子")
                
                # 为每条帖子爬取评论
                for post in posts:
                    crawler.crawl_comments(post.id, pages=1)
                    
    except Exception as e:
        print(f"定时爬取任务失败: {e}")

# 启动定时任务
def start_scheduled_tasks():
    """启动定时任务"""
    # 每小时执行一次爬取任务
    schedule.every().hour.do(crawl_task)
    
    # 启动后台线程运行定时任务
    def run_schedule():
        # 延迟执行，避免阻塞应用启动
        time.sleep(10)
        # 立即执行一次爬取任务
        crawl_task()
        
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    thread = threading.Thread(target=run_schedule, daemon=True)
    thread.start()
    print("定时爬取任务已启动")

# 只在直接运行该文件时执行
if __name__ == "__main__":
    start_scheduled_tasks()