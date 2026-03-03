#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试 MediaCrawler 集成效果
"""

from app.crawlers.weibo_crawler import WeiboCrawler

print("开始测试 MediaCrawler 关键词爬取")
crawler = WeiboCrawler(use_media_crawler=True)
print("开始爬取关键词: AI 技术")
posts = crawler.crawl_posts('AI 技术', pages=1)
print(f"成功爬取 {len(posts)} 条微博帖子")

if posts:
    print("前 3 条帖子:")
    for i, post in enumerate(posts[:3], 1):
        print(f"{i}. 作者: {post.author}")
        print(f"   内容: {post.content[:100]}...")
        print(f"   发布时间: {post.publish_time}")
        print(f"   点赞: {post.likes}, 评论: {post.comments_count}, 转发: {post.reposts}")
print("测试完成！")