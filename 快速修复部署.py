#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速修复并完成GitHub部署
"""

import os
import subprocess
import sys

def run_command(cmd, description=""):
    """运行命令并显示结果"""
    if description:
        print(f"\n[{description}]")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, 
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
    print("快速修复并完成GitHub部署")
    print("=" * 60)
    
    # 检查Git
    if not run_command("git --version", "检查Git"):
        print("\n✗ Git未安装，请先安装Git")
        input("按回车键退出...")
        return
    
    # 检查HTML文件
    if not os.path.exists('中际旭创_价格预测.html'):
        print("\n✗ 未找到HTML文件")
        print("请先运行: 运行预测模型.bat")
        input("按回车键退出...")
        return
    
    # 检查远程仓库
    print("\n[检查远程仓库]")
    result = subprocess.run("git remote -v", shell=True, capture_output=True, 
                          text=True, encoding='utf-8', errors='ignore')
    print(result.stdout)
    
    remote_url = "https://github.com/yishashawn/zhongji.git"
    
    # 验证仓库是否存在
    print(f"\n[验证仓库] {remote_url}")
    print("提示: 如果仓库不存在，会显示错误")
    print("如果提示输入凭据，请输入:")
    print("  用户名: 435256553@qq.com")
    print("  密码: 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")
    print()
    
    # 配置Git
    run_command("git config --global core.quotepath false", "配置Git编码")
    run_command("git config --global i18n.commitencoding utf-8", "配置Git编码")
    
    # 添加文件
    print("\n[添加文件]")
    files_to_add = [
        '中际旭创_价格预测.html',
        '中际旭创_价格预测模型.png',
        '中际旭创_多因素散点图.png',
        '中际旭创_特征重要性详细分析.png',
        'index.html'
    ]
    
    # 查找散点图文件
    scatter_files = [f for f in os.listdir('.') if f.startswith('中际旭创_所有因素散点图_') and f.endswith('.png')]
    files_to_add.extend(scatter_files)
    
    existing_files = [f for f in files_to_add if os.path.exists(f)]
    
    if not existing_files:
        print("✗ 没有找到需要上传的文件")
        input("按回车键退出...")
        return
    
    print(f"找到 {len(existing_files)} 个文件:")
    for f in existing_files:
        print(f"  ✓ {f}")
    
    # 逐个添加文件
    for file in existing_files:
        run_command(f'git add "{file}"', f"添加 {file}")
    
    # 提交
    print("\n[提交更改]")
    commit_msg = "更新中际旭创股票价格预测数据"
    run_command(f'git commit -m "{commit_msg}"', "提交")
    
    # 推送到GitHub
    print("\n" + "=" * 60)
    print("准备推送到GitHub")
    print("=" * 60)
    print("\n⚠️ 重要提示:")
    print("当提示输入凭据时:")
    print("  用户名: 435256553@qq.com")
    print("  密码: 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（粘贴Token）")
    print("\n注意: 密码处输入的是Token，不是GitHub密码！")
    print("=" * 60)
    
    choice = input("\n是否继续推送? (y/n): ").strip().lower()
    if choice != 'y':
        print("已取消")
        return
    
    # 推送
    print("\n[推送到GitHub]")
    success = run_command("git push -u origin main", "推送")
    
    if success:
        print("\n" + "=" * 60)
        print("部署成功！")
        print("=" * 60)
        print("\n您的网站地址:")
        print("  https://yishashawn.github.io/zhongji/")
        print("\n注意: 如果网站无法访问，请:")
        print("1. 访问: https://github.com/yishashawn/zhongji/settings/pages")
        print("2. Source: 选择 main 和 / (root)")
        print("3. Save")
        print("4. 等待1-5分钟生效")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("推送失败")
        print("=" * 60)
        print("\n可能的原因:")
        print("1. 仓库不存在 - 请访问 https://github.com/new 创建仓库")
        print("2. Token错误 - 请检查Token是否正确")
        print("3. Token权限不足 - 确保Token权限包含 'repo'")
        print("=" * 60)
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()

