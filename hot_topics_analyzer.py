#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
热点数据分析与推送系统
功能：自动获取百度热搜数据，通过DeepSeek API进行智能分析，生成报告并发送邮件
"""

import os
import json
import requests
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from openai import OpenAI
import yagmail
from dotenv import load_dotenv
import base64  # 用于图片编码
# 设置图片清晰度
plt.rcParams['figure.dpi'] = 300
# 设置中文字体
font_path = './fonts/SimHei.ttf'
font_prop = fm.FontProperties(fname=font_path)
# 将字体名称添加到系统字体列表
fm.fontManager.addfont(font_path)
# 设置全局字体
plt.rcParams['font.sans-serif'] = ['SimHei']

# 解决负号显示问题
plt.rcParams['axes.unicode_minus'] = False

load_dotenv()

class HotTopicsAnalyzer:
    """热点数据分析与推送系统"""
    
    def __init__(self):
        """初始化系统配置"""
        # API配置
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_base_url = "https://api.deepseek.com"
        
        # 邮件配置
        self.email_user = os.getenv("EMAIL_USER")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.email_host = os.getenv("EMAIL_HOST")
        self.email_recipients = os.getenv("EMAIL_RECIPIENTS", "").split(",")
        
        # 数据存储路径
        self.data_dir = "data"
        self.report_dir = "reports"
        
        # 创建必要的目录
        for directory in [self.data_dir, self.report_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
        # OpenAI客户端配置
        if self.deepseek_api_key:
            self.ai_client = OpenAI(
                api_key=self.deepseek_api_key,
                base_url=self.deepseek_base_url
            )
        else:
            print("警告: 未设置DEEPSEEK_API_KEY环境变量，AI分析功能将不可用")
            self.ai_client = None
    
    def get_baidu_hot(self):
        """获取百度热搜数据"""
        url = "https://top.baidu.com/api/board?platform=wise&tab=realtime"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            hot_topics = []
            for item in data.get("data", {}).get("cards", [{}])[0].get("content", []):
                topic = {
                    "title": item.get("word"),
                    "url": item.get("url"),
                    "hot_score": item.get("hotScore")
                }
                hot_topics.append(topic)
            
            print(f"成功获取{len(hot_topics)}个百度热搜话题")
            return hot_topics[:10]  # 返回前10个热点
        
        except Exception as e:
            print(f"获取百度热搜失败: {e}")
            return []
    
    def save_hot_topics(self, hot_topics):
        """保存热搜数据到本地文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.data_dir}/baidu_hot_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(hot_topics, f, ensure_ascii=False, indent=2)
        
        print(f"热搜数据已保存到: {filename}")
        return filename
    
    def analyze_with_ai(self, hot_topics):
        """使用DeepSeek API分析热搜数据"""
        if not self.ai_client:
            return "AI分析功能未启用，请设置DEEPSEEK_API_KEY环境变量"
        
        # 构建提示词
        topics_text = "\n".join([f"{i+1}. {item['title']} (热度: {item['hot_score']})" 
                              for i, item in enumerate(hot_topics)])
        
        prompt = f"""
        以下是当前百度热搜前10名话题:
        
        {topics_text}
        
        请针对这些热搜话题进行深度分析，包括：
        1. 热点话题分类与趋势分析
        2. 社会关注点与公众情绪分析
        3. 背后的社会意义与影响
        4. 对市场营销和内容创作的启示
        
        请生成一份结构清晰、见解深刻的分析报告，字数在800字左右。
        """
        
        try:
            response = self.ai_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一位专业的数据分析师和趋势洞察专家"},
                    {"role": "user", "content": prompt},
                ],
                stream=False
            )
            
            analysis_result = response.choices[0].message.content
            print("AI分析完成")
            return analysis_result
            
        except Exception as e:
            print(f"AI分析失败: {e}")
            return f"AI分析过程中出现错误: {str(e)}"
    
    def generate_visualization(self, hot_topics):
        """生成热搜数据可视化图表"""
        if not hot_topics:
            return None
            
        # 提取数据
        titles = [item['title'] for item in hot_topics]
        scores = [item['hot_score'] for item in hot_topics]
        
        # 为了使图表更美观，将标题截断
        short_titles = [title[:10] + '...' if len(title) > 10 else title for title in titles]
        
        # 创建水平条形图
        plt.figure(figsize=(10, 8))
        plt.barh(short_titles[::-1], scores[::-1], color='#FF9999')
        plt.xlabel('热度指数')
        plt.title('百度热搜榜 TOP 10', fontsize=16)
        plt.tight_layout()
        
        # 保存图表
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chart_path = f"{self.data_dir}/hot_chart_{timestamp}.png"
        plt.savefig(chart_path, dpi=100)
        plt.close()
        
        print(f"热搜可视化图表已保存到: {chart_path}")
        return chart_path
    
    def create_report(self, hot_topics, analysis, chart_path=None):
        """创建完整报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_date = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        report_file = f"{self.report_dir}/热点分析报告_{timestamp}.html"
        
        # 构建热搜列表HTML
        topics_html = ""
        for i, topic in enumerate(hot_topics):
            topics_html += f"""
            <tr>
                <td>{i+1}</td>
                <td><a href="{topic['url']}" target="_blank">{topic['title']}</a></td>
                <td>{topic['hot_score']}</td>
            </tr>
            """
        
        # 处理分析文本，将换行符替换为HTML换行标签
        analysis_html = analysis.replace('\n', '<br>')
        
        # 图片处理 - 将图片转为base64编码
        image_html = ''
        if chart_path and os.path.exists(chart_path):
            with open(chart_path, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                image_html = f'<div class="chart"><img src="data:image/png;base64,{img_base64}" alt="热搜榜可视化"></div>'
        
        # 构建完整HTML报告
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>热点分析报告 - {report_date}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 1000px; margin: 0 auto; padding: 20px; }}
                h1, h2 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .chart {{ text-align: center; margin: 20px 0; }}
                .chart img {{ max-width: 100%; height: auto; }}
                .analysis {{ background-color: #f8f8f8; padding: 15px; border-left: 4px solid #FF9999; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #777; text-align: center; }}
            </style>
        </head>
        <body>
            <h1>热点分析报告</h1>
            <p>生成时间: {report_date}</p>
            
            <h2>百度热搜榜 TOP 10</h2>
            <table>
                <tr>
                    <th>排名</th>
                    <th>话题</th>
                    <th>热度</th>
                </tr>
                {topics_html}
            </table>
            
            {image_html}
            
            <h2>热点深度分析</h2>
            <div class="analysis">
                <p>{analysis_html}</p>
            </div>
            
            <div class="footer">
                <p>本报告由热点数据分析与推送系统自动生成</p>
            </div>
        </body>
        </html>
        """
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"分析报告已保存到: {report_file}")
        return report_file
    
    def send_email(self, report_file, chart_path=None):
        """发送邮件推送报告"""
        if not self.email_user or not self.email_password or not self.email_recipients:
            print("邮件配置不完整，跳过发送")
            return False
        
        try:
            # 创建邮件客户端
            yag = yagmail.SMTP(self.email_user, self.email_password, self.email_host)
            
            # 邮件主题
            subject = f"热点分析报告 - {datetime.now().strftime('%Y年%m月%d日')}"
            
            # 邮件正文
            contents = [
                "您好，",
                "附件是最新的热点分析报告，请查收。",
                report_file
            ]
            
            # 如果有图表，添加到附件
            if chart_path:
                contents.append(chart_path)
            
            # 发送邮件
            yag.send(to=self.email_recipients, subject=subject, contents=contents)
            yag.close()
            
            print(f"分析报告已成功发送至: {', '.join(self.email_recipients)}")
            return True
            
        except Exception as e:
            print(f"发送邮件失败: {e}")
            return False
    
    def run(self):
        """执行完整的热点分析与推送流程"""
        print(f"=== 热点数据分析与推送系统启动 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
        
        # 1. 获取百度热搜数据
        hot_topics = self.get_baidu_hot()
        if not hot_topics:
            print("未获取到热搜数据，程序终止")
            return

        # 2. 保存热搜数据
        self.save_hot_topics(hot_topics)

        # 3. 生成可视化图表
        chart_path = self.generate_visualization(hot_topics)
        # 4. AI分析热搜数据
        analysis = self.analyze_with_ai(hot_topics)

        # 5. 创建完整报告
        report_file = self.create_report(hot_topics, analysis, chart_path)
        
        # 6. 发送邮件
        self.send_email(report_file, chart_path)
        
        print(f"=== 热点数据分析与推送完成 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")


if __name__ == "__main__":
    analyzer = HotTopicsAnalyzer()
    analyzer.run()
