#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 MediaCrawler 集成效果
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.crawlers.weibo_crawler import WeiboCrawler

def test_media_crawler():
    """测试 MediaCrawler 功能"""
    print("=" * 60)
    print("测试 MediaCrawler 集成效果")
    print("=" * 60)
    
    try:
        # 创建爬虫实例，启用 MediaCrawler
        crawler = WeiboCrawler(use_media_crawler=True)
        print("\n1. 测试爬取微博热搜")
        print("-" * 40)
        hot_topics = crawler.crawl_hot_topics()
        print(f"成功爬取 {len(hot_topics)} 个热搜话题")
        if hot_topics:
            print("前 5 个热搜:")
            for i, topic in enumerate(hot_topics[:5], 1):
                print(f"{i}. {topic['title']} - {topic['heat']}")
        
        print("\n2. 测试爬取特定关键词")
        print("-" * 40)
        keyword = "AI 技术"
        pages = 2
        print(f"爬取关键词: {keyword}, 页数: {pages}")
        posts = crawler.crawl_posts(keyword, pages)
        print(f"成功爬取 {len(posts)} 条微博帖子")
        if posts:
            print("前 3 条帖子:")
            for i, post in enumerate(posts[:3], 1):
                print(f"{i}. 作者: {post.author}")
                print(f"   内容: {post.content[:100]}...")
                print(f"   发布时间: {post.publish_time}")
                print(f"   点赞: {post.likes}, 评论: {post.comments_count}, 转发: {post.reposts}")
        
        print("\n3. 测试传统爬虫（备用方案）")
        print("-" * 40)
        # 创建不使用 MediaCrawler 的爬虫实例
        traditional_crawler = WeiboCrawler(use_media_crawler=False)
        traditional_posts = traditional_crawler.crawl_posts(keyword, pages=1)
        print(f"传统爬虫成功爬取 {len(traditional_posts)} 条微博帖子")
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        print("\n总结:")
        print(f"- MediaCrawler 爬取热搜: {'成功' if hot_topics else '失败'}")
        print(f"- MediaCrawler 爬取关键词: {'成功' if posts else '失败'}")
        print(f"- 传统爬虫备用方案: {'成功' if traditional_posts else '失败'}")
        
        if hot_topics or posts:
            print("\n✅ MediaCrawler 集成测试通过！")
        else:
            print("\n❌ MediaCrawler 集成测试失败，请检查配置！")
            
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        print("\n❌ MediaCrawler 集成测试失败！")

if __name__ == "__main__":
    test_media_crawler()