# MediaCrawler 集成指南

## 简介

本指南详细介绍如何在微博舆情分析系统中集成 MediaCrawler 技术，以提升微博数据爬取能力。MediaCrawler 是一个功能强大的媒体爬虫工具，支持多种平台，包括微博。

## 集成优势

1. **提高爬取成功率**：使用浏览器自动化技术，能够绕过微博的反爬机制
2. **获取更多内容**：支持登录态管理，可获取需要登录才能查看的内容
3. **无需 JS 逆向**：通过浏览器执行 JavaScript 自动获取签名参数
4. **支持 IP 代理**：可配置代理池，进一步降低被封概率
5. **完善的错误处理**：内置重试机制和错误处理

## 前置依赖

在安装 MediaCrawler 之前，需要确保系统已安装以下依赖：

### 1. Node.js

MediaCrawler 基于 Node.js 开发，需要安装 Node.js 16.0 或更高版本。

- **Windows**: 从 [Node.js 官网](https://nodejs.org/zh-cn/) 下载并安装
- **Linux**: 使用包管理器安装，如 `apt install nodejs npm`
- **macOS**: 使用 Homebrew 安装，如 `brew install node`

安装完成后，验证版本：

```bash
node -v
npm -v
```

### 2. Python 依赖

确保系统已安装以下 Python 包：

```bash
pip install flask flask-login werkzeug beautifulsoup4 requests
```

## 安装步骤

### 1. 克隆 MediaCrawler 项目

在项目根目录下执行以下命令：

```bash
# 进入项目根目录
cd e:\舆情分析系统\2

# 克隆 MediaCrawler 项目
git clone https://github.com/NanmiCoder/MediaCrawler.git

# 进入 MediaCrawler 目录
cd MediaCrawler

# 安装依赖
npm install
```

### 2. 配置 MediaCrawler

1. **创建配置文件**：复制 `config.example.js` 为 `config.js`
2. **配置代理**（可选）：在 `config.js` 中配置代理设置
3. **配置登录信息**（可选）：在 `config.js` 中配置微博登录信息，以获取更多内容

### 3. 测试 MediaCrawler

在 MediaCrawler 目录下执行以下命令，测试基本功能：

```bash
# 测试爬取微博热搜
node index.js --platform weibo --type hot

# 测试爬取特定关键词
node index.js --platform weibo --keyword "AI 技术" --pages 2
```

## 系统集成

### 1. 适配器模块

系统已内置 `MediaCrawlerAdapter` 模块，位于 `app/crawlers/media_crawler_adapter.py`，负责：

- 执行 MediaCrawler 命令
- 解析爬取结果
- 转换为系统数据模型
- 存储到数据库

### 2. 爬虫模块改造

`app/crawlers/weibo_crawler.py` 已改造为支持 MediaCrawler：

- 添加 `use_media_crawler` 参数，默认为 `False`
- 当启用 MediaCrawler 时，使用适配器爬取数据
- 当 MediaCrawler 不可用时，自动回退到传统爬虫

### 3. 路由配置

`app/routes.py` 中的 `crawl` 路由已默认启用 MediaCrawler：

```python
# 默认使用 MediaCrawler
crawler = WeiboCrawler(use_media_crawler=True)
```

## 使用指南

### 1. 通过 Web 界面使用

1. 登录系统
2. 点击左侧菜单中的「数据爬取」
3. 在搜索框中输入关键词，选择爬取页数
4. 点击「开始爬取」按钮
5. 查看爬取结果

### 2. 通过命令行测试

执行以下命令测试 MediaCrawler 集成效果：

```bash
# 进入项目目录
cd e:\舆情分析系统\2\weibo_sentiment_analysis

# 运行测试脚本
python test_media_crawler.py
```

### 3. 配置选项

#### MediaCrawler 路径配置

默认情况下，系统会在项目根目录下查找 MediaCrawler 目录。如果您将 MediaCrawler 安装在其他位置，可以在创建 `WeiboCrawler` 实例时指定路径：

```python
crawler = WeiboCrawler(
    use_media_crawler=True,
    media_crawler_path="/path/to/MediaCrawler"
)
```

#### 爬取参数配置

- **keyword**: 搜索关键词
- **pages**: 爬取页数，默认为 5
- **crawl_comments**: 是否爬取评论，默认为 `False`

## 故障排除

### 1. MediaCrawler 执行失败

**症状**：测试脚本显示 "MediaCrawler 执行失败"

**解决方案**：
- 检查 Node.js 是否正确安装
- 检查 MediaCrawler 依赖是否安装完成
- 检查 MediaCrawler 目录路径是否正确
- 查看错误信息，根据具体错误进行修复

### 2. 爬取结果为空

**症状**：爬取成功但返回空结果

**解决方案**：
- 检查网络连接是否正常
- 尝试配置代理 IP
- 尝试配置微博登录信息
- 检查关键词是否正确

### 3. 系统回退到传统爬虫

**症状**：日志显示 "使用传统方法爬取"

**解决方案**：
- 检查 MediaCrawler 是否正确安装
- 检查 MediaCrawler 是否能正常运行
- 检查 MediaCrawler 路径是否正确

## 性能优化

1. **启用登录态缓存**：在 MediaCrawler 配置中启用登录态缓存，减少登录次数
2. **配置代理池**：使用代理池，降低被封概率
3. **调整爬取间隔**：在 MediaCrawler 配置中调整爬取间隔，避免请求过于频繁
4. **使用多线程**：对于大规模爬取，可考虑使用多线程并行爬取

## 安全注意事项

1. **不要频繁爬取**：遵守网站 robots.txt 规则，不要过于频繁地爬取数据
2. **保护登录信息**：如果配置了微博登录信息，确保配置文件安全，不要提交到版本控制系统
3. **使用合法代理**：如果使用代理 IP，确保使用合法的代理服务
4. **控制爬取规模**：合理控制爬取数据量，避免对目标网站造成过大压力

## 常见问题

### Q: MediaCrawler 与传统爬虫有什么区别？

**A**：MediaCrawler 使用浏览器自动化技术，能够执行 JavaScript，绕过反爬机制，获取更多内容。传统爬虫基于简单的 HTTP 请求，容易被反爬机制识别。

### Q: 为什么有时爬取结果会不一致？

**A**：微博的页面结构和 API 可能会动态变化，导致爬取结果不一致。MediaCrawler 会定期更新以适应这些变化。

### Q: 如何提高爬取速度？

**A**：可以通过以下方式提高爬取速度：
- 配置更稳定的代理池
- 启用登录态缓存
- 调整爬取间隔（注意不要过于频繁）
- 使用多线程并行爬取

### Q: 爬取的数据如何存储？

**A**：爬取的数据会存储到系统的 SQLite 数据库中，具体表结构如下：
- `users`: 存储用户信息
- `weibo_posts`: 存储微博帖子信息
- `weibo_comments`: 存储微博评论信息

## 总结

通过集成 MediaCrawler 技术，微博舆情分析系统的爬取能力得到了显著提升，能够更稳定、更全面地获取微博数据。同时，系统保留了传统爬虫作为备用方案，确保在 MediaCrawler 不可用时仍能正常工作。

如果您在集成过程中遇到任何问题，请参考本指南的故障排除部分，或查阅 MediaCrawler 的官方文档。

---

**版本**: 1.0.0
**更新时间**: 2024-01-01
**维护者**: 系统开发团队