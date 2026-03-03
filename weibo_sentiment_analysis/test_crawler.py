from app.crawlers.weibo_crawler import WeiboCrawler

# 创建爬虫实例
crawler = WeiboCrawler()

# 测试爬取微博帖子
print("开始爬取微博帖子...")
posts = crawler.crawl_posts('人工智能', pages=2)
print(f"爬取完成，获取了 {len(posts)} 条微博帖子")

# 测试爬取热搜话题
print("\n开始爬取热搜话题...")
hot_topics = crawler.crawl_hot_topics()
print(f"爬取完成，获取了 {len(hot_topics)} 个热搜话题")
for topic in hot_topics[:5]:
    print(f"- {topic['title']}: {topic['heat']}")

print("\n爬虫测试完成！")