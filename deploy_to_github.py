#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
部署到GitHub Pages
"""

import os
import subprocess
import sys

# 导入subprocess用于run_cmd函数

def run_cmd(cmd_list, description=""):
    """运行命令"""
    if description:
        print(f"\n[{description}]")
    try:
        result = subprocess.run(cmd_list, capture_output=True, 
                              text=True, encoding='utf-8', errors='ignore', timeout=30)
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(f"错误: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"执行失败: {e}")
        return False

def main():
    print("=" * 60)
    print("部署到GitHub Pages")
    print("=" * 60)
    
    # 配置远程仓库
    print("\n[配置远程仓库]")
    run_cmd(['git', 'remote', 'remove', 'origin'], "移除旧远程")
    run_cmd(['git', 'remote', 'add', 'origin', 'https://github.com/yishashawn/stock-prediction.git'], "添加新远程")
    run_cmd(['git', 'remote', '-v'], "查看远程")
    
    # 配置Git
    print("\n[配置Git]")
    run_cmd(['git', 'config', '--global', 'core.quotepath', 'false'])
    run_cmd(['git', 'config', '--global', 'i18n.commitencoding', 'utf-8'])
    
    # 查找文件
    print("\n[查找文件]")
    files_to_add = []
    
    # HTML文件
    html_file = '中际旭创_价格预测.html'
    if os.path.exists(html_file):
        files_to_add.append(html_file)
        print(f"  ✓ {html_file}")
    else:
        print(f"  ✗ {html_file} 不存在")
    
    # index.html
    if os.path.exists('index.html'):
        files_to_add.append('index.html')
        print(f"  ✓ index.html")
    else:
        print("  ℹ index.html 不存在，将创建")
        # 创建index.html
        index_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="0; url=中际旭创_价格预测.html">
    <title>中际旭创股票价格预测</title>
</head>
<body>
    <h1>正在跳转...</h1>
    <p><a href="中际旭创_价格预测.html">点击这里访问预测页面</a></p>
</body>
</html>"""
        try:
            with open('index.html', 'w', encoding='utf-8') as f:
                f.write(index_content)
            files_to_add.append('index.html')
            print("  ✓ index.html 已创建")
        except Exception as e:
            print(f"  ✗ 创建index.html失败: {e}")
    
    # PNG文件
    png_files = [
        '中际旭创_价格预测模型.png',
        '中际旭创_多因素散点图.png',
        '中际旭创_特征重要性详细分析.png'
    ]
    
    for png in png_files:
        if os.path.exists(png):
            files_to_add.append(png)
            print(f"  ✓ {png}")
    
    # 散点图文件
    for f in os.listdir('.'):
        if f.startswith('中际旭创_所有因素散点图_') and f.endswith('.png'):
            files_to_add.append(f)
            print(f"  ✓ {f}")
    
    if not files_to_add:
        print("\n✗ 没有找到需要上传的文件")
        input("按回车键退出...")
        return
    
    # 添加文件（强制添加）
    print(f"\n[添加文件] 共 {len(files_to_add)} 个文件")
    for f in files_to_add:
        result = subprocess.run(['git', 'add', '-f', f], capture_output=True, 
                              text=True, encoding='utf-8', errors='ignore', timeout=10)
        if result.returncode == 0:
            print(f"  ✓ {f}")
        else:
            print(f"  ✗ {f} - {result.stderr}")
    
    # 检查是否有文件被添加
    result = subprocess.run(['git', 'status', '--short'], capture_output=True,
                          text=True, encoding='utf-8', errors='ignore')
    staged_files = [line for line in result.stdout.split('\n') if line.startswith('A ') or line.startswith('M ')]
    
    if not staged_files:
        print("\n⚠️ 警告: 没有文件被添加到暂存区")
        print("可能这些文件已经在之前的提交中")
        print("尝试强制添加所有文件...")
        run_cmd(['git', 'add', '-A'], "添加所有文件")
    
    # 提交
    print("\n[提交更改]")
    commit_msg = "首次部署：中际旭创股票价格预测"
    result = run_cmd(['git', 'commit', '-m', commit_msg], "提交")
    
    if not result:
        # 如果没有更改，尝试创建空提交或检查状态
        print("检查提交状态...")
        run_cmd(['git', 'status'], "Git状态")
    
    # 推送
    print("\n" + "=" * 60)
    print("准备推送到GitHub")
    print("=" * 60)
    print("\n⚠️ 重要提示:")
    print("当提示输入凭据时:")
    print("  用户名: 435256553@qq.com")
    print("  密码: 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")
    print("\n注意: 密码处输入的是Token，不是GitHub密码！")
    print("=" * 60)
    
    # 自动继续（不等待用户输入）
    print("\n自动继续推送...")
    
    # 推送
    print("\n[推送到GitHub]")
    success = run_cmd(['git', 'push', '-u', 'origin', 'main'], "推送")
    
    if success:
        print("\n" + "=" * 60)
        print("部署成功！")
        print("=" * 60)
        print("\n您的网站地址:")
        print("  https://yishashawn.github.io/stock-prediction/")
        print("\n下一步: 启用GitHub Pages")
        print("1. 访问: https://github.com/yishashawn/stock-prediction/settings/pages")
        print("2. Source: 选择 main 和 / (root)")
        print("3. 点击 Save")
        print("4. 等待1-5分钟，网站即可访问")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("推送失败")
        print("=" * 60)
        print("\n可能的原因:")
        print("1. Token错误或过期")
        print("2. Token权限不足（需要 'repo' 权限）")
        print("3. 网络问题")
        print("=" * 60)
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()

