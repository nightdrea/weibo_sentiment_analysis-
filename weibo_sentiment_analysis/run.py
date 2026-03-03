from app import app, start_tasks

if __name__ == '__main__':
    # 启动定时爬取任务
    start_tasks()
    # 优化启动配置，使用 0.0.0.0 监听所有网络接口，端口使用 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
