# 热点数据分析与推送系统

这是一个自动化的热点数据采集、分析和推送系统，可以实时获取百度热搜数据，通过人工智能进行深度分析，生成精美报告并通过邮件推送。

## 功能特点

- 自动爬取百度热搜榜前十名话题
- 通过DeepSeek AI进行热点深度分析
- 生成可视化图表直观展示热度分布
- 创建美观的HTML分析报告
- 支持邮件自动推送功能
- 数据和报告本地存档

## 系统架构

系统主要由以下模块组成：

1. **数据采集模块**：负责从百度热搜API获取实时热点数据
2. **数据存储模块**：将获取的热点数据保存为JSON格式文件
3. **数据可视化模块**：生成热搜榜热度分布图表
4. **AI分析模块**：调用DeepSeek API进行热点深度分析
5. **报告生成模块**：创建包含热搜榜、图表和分析结果的HTML报告
6. **邮件推送模块**：将生成的报告通过邮件发送给指定收件人

## 安装与配置

### 环境要求

- Python 3.8+
- 安装所需依赖包

### 安装步骤

1. 克隆或下载本项目到本地

2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```

3. 配置环境变量：
   - 复制`.env.example`文件并重命名为`.env`
   - 编辑`.env`文件，填入你的DeepSeek API密钥和邮件配置信息

### 环境变量说明

| 环境变量 | 描述 | 示例值 |
|---------|------|-------|
| DEEPSEEK_API_KEY | DeepSeek AI平台的API密钥 | sk-xxxxxxxxxxxxxxxx |
| EMAIL_USER | 发送邮件的邮箱地址 | your_email@example.com |
| EMAIL_PASSWORD | 邮箱密码或应用专用密码 | password_or_app_password |
| EMAIL_RECIPIENTS | 接收报告的邮箱地址(多个用逗号分隔) | user1@example.com,user2@example.com |

## 使用方法

### 基本用法

直接运行主程序：

```bash
python hot_topics_analyzer.py
```

系统将自动执行以下流程：
1. 获取百度热搜数据
2. 保存数据到`data`目录
3. 生成可视化图表
4. 通过AI进行热点分析
5. 创建HTML分析报告并保存到`reports`目录
6. 发送邮件(如果配置了邮件信息)

### 定时任务设置

可以使用系统的定时任务工具(如crontab、Windows计划任务)设置定期运行：

#### Linux/MacOS (Crontab)

```bash
# 每天上午9点和下午5点运行
0 9,17 * * * cd /path/to/project && python hot_topics_analyzer.py
```

#### Windows (Task Scheduler)

创建一个批处理文件`run_analyzer.bat`：

```batch
@echo off
cd /d "D:\path\to\project"
python hot_topics_analyzer.py
```

然后在Windows任务计划程序中设置定时运行此批处理文件。

## 目录结构

```
├── hot_topics_analyzer.py  # 主程序
├── requirements.txt        # 依赖包列表
├── .env.example           # 环境变量示例文件
├── README.md              # 项目说明文档
├── data/                  # 存储热搜数据和图表
└── reports/               # 存储生成的分析报告
```

## API说明

主要类`HotTopicsAnalyzer`包含以下方法：

| 方法 | 描述 |
|------|------|
| `get_baidu_hot()` | 获取百度热搜数据 |
| `save_hot_topics(hot_topics)` | 保存热搜数据到本地文件 |
| `analyze_with_ai(hot_topics)` | 使用DeepSeek AI分析热搜数据 |
| `generate_visualization(hot_topics)` | 生成热搜数据可视化图表 |
| `create_report(hot_topics, analysis, chart_path)` | 创建完整HTML报告 |
| `send_email(report_file, chart_path)` | 发送邮件推送报告 |
| `run()` | 执行完整的热点分析与推送流程 |

## 常见问题

### Q: 如何更改热搜数据来源?
A: 可以修改`get_baidu_hot()`方法，替换为其他热搜API的实现。

### Q: 报告格式如何自定义?
A: 在`create_report()`方法中修改HTML模板和CSS样式。

### Q: 邮件发送失败怎么办?
A: 检查邮箱配置是否正确，对于Gmail等服务可能需要使用应用专用密码而非账户密码。

## 注意事项

- DeepSeek API调用可能产生费用，请关注您的API使用量和账单
- 爬虫使用请遵守相关网站的robots.txt规定和使用条款
- 定期清理data和reports目录，避免占用过多磁盘空间
