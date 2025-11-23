#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
启动本地Web服务器，让其他人可以通过网络访问中际旭创价格预测网页
"""

import http.server
import socketserver
import socket
import webbrowser
import os
import sys

# 设置端口
PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """自定义HTTP请求处理器，支持中文文件名"""
    
    def end_headers(self):
        # 添加CORS头，允许跨域访问
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def log_message(self, format, *args):
        # 自定义日志格式
        print(f"[{self.log_date_time_string()}] {format % args}")

def get_local_ip():
    """获取本机IP地址"""
    try:
        # 连接到一个远程地址来获取本机IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def main():
    # 切换到脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 检查HTML文件是否存在
    html_file = "中际旭创_价格预测.html"
    if not os.path.exists(html_file):
        print(f"错误: 找不到文件 {html_file}")
        print("请先运行 predict_stock_price_advanced.py 生成HTML文件")
        input("按回车键退出...")
        sys.exit(1)
    
    # 获取本机IP地址
    local_ip = get_local_ip()
    
    print("=" * 60)
    print("中际旭创股票价格预测 - Web服务器")
    print("=" * 60)
    print(f"\n服务器正在启动...")
    print(f"\n访问地址:")
    print(f"  本地访问: http://localhost:{PORT}/中际旭创_价格预测.html")
    print(f"  本地访问: http://127.0.0.1:{PORT}/中际旭创_价格预测.html")
    print(f"  局域网访问: http://{local_ip}:{PORT}/中际旭创_价格预测.html")
    print(f"\n分享给其他人:")
    print(f"  将以下地址发送给同一局域网内的其他人:")
    print(f"  http://{local_ip}:{PORT}/中际旭创_价格预测.html")
    print(f"\n注意:")
    print(f"  - 确保防火墙允许端口 {PORT} 的访问")
    print(f"  - 其他人需要与您在同一个局域网内（同一WiFi/网络）")
    print(f"  - 按 Ctrl+C 停止服务器")
    print("=" * 60)
    print("\n正在启动服务器...\n")
    
    try:
        # 创建服务器
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            # 自动打开浏览器
            try:
                url = f"http://localhost:{PORT}/中际旭创_价格预测.html"
                webbrowser.open(url)
            except:
                pass
            
            print(f"服务器已启动，正在监听端口 {PORT}...")
            print("等待访问请求...\n")
            
            # 启动服务器
            httpd.serve_forever()
            
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n错误: 端口 {PORT} 已被占用")
            print(f"请关闭占用该端口的程序，或修改脚本中的 PORT 变量")
        else:
            print(f"\n错误: {e}")
        input("\n按回车键退出...")
    except KeyboardInterrupt:
        print("\n\n服务器已停止")
        print("感谢使用！")
    except Exception as e:
        print(f"\n发生错误: {e}")
        input("\n按回车键退出...")

if __name__ == "__main__":
    main()

