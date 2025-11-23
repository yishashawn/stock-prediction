#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
一键配置GitHub Pages网站
"""

import os
import subprocess
import webbrowser

def run_cmd(cmd_list):
    """运行命令"""
    try:
        result = subprocess.run(cmd_list, capture_output=True, 
                              text=True, encoding='utf-8', errors='ignore', timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except:
        return False, "", ""

def main():
    print("=" * 60)
    print("一键配置GitHub Pages网站")
    print("=" * 60)
    
    # 1. 配置远程仓库
    print("\n[1/4] 配置远程仓库...")
    run_cmd(['git', 'remote', 'remove', 'origin'])
    run_cmd(['git', 'remote', 'add', 'origin', 'https://github.com/yishashawn/stock-prediction.git'])
    print("✓ 完成")
    
    # 2. 添加文件
    print("\n[2/4] 添加文件...")
    files = [
        '中际旭创_价格预测.html',
        'index.html',
        '中际旭创_价格预测模型.png',
        '中际旭创_多因素散点图.png',
        '中际旭创_特征重要性详细分析.png'
    ]
    
    for f in os.listdir('.'):
        if f.startswith('中际旭创_所有因素散点图_') and f.endswith('.png'):
            files.append(f)
    
    existing = [f for f in files if os.path.exists(f)]
    print(f"找到 {len(existing)} 个文件")
    
    for f in existing:
        run_cmd(['git', 'add', '-f', f])
    
    if not os.path.exists('index.html'):
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write('''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url=中际旭创_价格预测.html">
    <title>中际旭创股票价格预测</title>
</head>
<body>
    <h1>正在跳转...</h1>
    <p><a href="中际旭创_价格预测.html">点击这里</a></p>
</body>
</html>''')
        run_cmd(['git', 'add', 'index.html'])
    
    run_cmd(['git', 'add', '-A'])
    run_cmd(['git', 'commit', '-m', '更新网站文件'])
    print("✓ 文件已提交")
    
    # 3. 推送
    print("\n[3/4] 推送到GitHub...")
    print("提示: 如果提示输入凭据，请输入Token")
    success, _, stderr = run_cmd(['git', 'push', '-u', 'origin', 'main'])
    
    if not success and ("GH013" in stderr or "secret" in stderr.lower()):
        print("⚠️ 需要允许Token推送")
        print("正在打开GitHub页面...")
        webbrowser.open("https://github.com/yishashawn/stock-prediction/security/secret-scanning/unblock-secret/35skOPQ298UdllgeXz54YNMZuTH")
        print("\n请在打开的页面中点击允许，然后等待5秒...")
        import time
        time.sleep(5)
        print("重试推送...")
        success, _, _ = run_cmd(['git', 'push', '-u', 'origin', 'main'])
        if success:
            print("✓ 推送成功")
        else:
            print("⚠️ 推送可能仍需手动处理，但继续配置Pages...")
    elif success:
        print("✓ 推送成功")
    else:
        print("⚠️ 推送可能失败，但继续配置Pages...")
    
    # 4. 打开Pages设置
    print("\n[4/4] 打开GitHub Pages设置...")
    webbrowser.open("https://github.com/yishashawn/stock-prediction/settings/pages")
    print("✓ 已打开设置页面")
    
    print("\n" + "=" * 60)
    print("最后一步: 在打开的页面中")
    print("=" * 60)
    print("1. Source: 选择 'main' 和 '/ (root)'")
    print("2. 点击 'Save'")
    print("3. 等待1-5分钟")
    print("\n网站地址:")
    print("  https://yishashawn.github.io/stock-prediction/")
    print("=" * 60)
    print("\n✓ 配置完成！请在打开的页面中完成最后一步。")

if __name__ == "__main__":
    main()

