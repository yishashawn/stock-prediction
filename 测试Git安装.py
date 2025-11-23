#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试Git是否已正确安装并配置
"""

import subprocess
import os
import sys

def test_git():
    """测试Git是否可用"""
    print("=" * 60)
    print("Git 安装测试")
    print("=" * 60)
    
    # 测试1: 检查git命令
    print("\n1. 检查git命令...")
    try:
        result = subprocess.run(['git', '--version'], 
                               capture_output=True, 
                               text=True, 
                               timeout=5)
        if result.returncode == 0:
            print(f"   ✓ Git已安装: {result.stdout.strip()}")
            git_version = result.stdout.strip()
        else:
            print("   ✗ Git命令执行失败")
            return False
    except FileNotFoundError:
        print("   ✗ Git未找到，可能的原因:")
        print("     - Git未正确安装")
        print("     - Git未添加到PATH环境变量")
        print("     - 需要重启PowerShell/命令提示符")
        print("\n   解决方法:")
        print("     1. 确认Git已安装")
        print("     2. 关闭并重新打开PowerShell/命令提示符")
        print("     3. 或重启电脑")
        return False
    except Exception as e:
        print(f"   ✗ 检查Git时出错: {e}")
        return False
    
    # 测试2: 检查Git配置
    print("\n2. 检查Git配置...")
    try:
        result = subprocess.run(['git', 'config', '--global', 'user.email'],
                               capture_output=True,
                               text=True,
                               timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            email = result.stdout.strip()
            print(f"   ✓ 用户邮箱: {email}")
        else:
            print("   ⚠ 用户邮箱未配置")
            print("   建议运行: git config --global user.email \"435256553@qq.com\"")
        
        result = subprocess.run(['git', 'config', '--global', 'user.name'],
                               capture_output=True,
                               text=True,
                               timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            name = result.stdout.strip()
            print(f"   ✓ 用户名: {name}")
        else:
            print("   ⚠ 用户名未配置")
            print("   建议运行: git config --global user.name \"syy\"")
    except Exception as e:
        print(f"   ✗ 检查配置时出错: {e}")
    
    # 测试3: 检查当前目录
    print("\n3. 检查当前目录...")
    current_dir = os.getcwd()
    print(f"   当前目录: {current_dir}")
    
    if os.path.exists('中际旭创_价格预测.html'):
        print("   ✓ 找到HTML文件")
    else:
        print("   ✗ 未找到HTML文件")
        print("   请先运行 predict_stock_price_advanced.py 生成HTML文件")
    
    if os.path.exists('.git'):
        print("   ✓ 当前目录是Git仓库")
    else:
        print("   ℹ 当前目录不是Git仓库（部署脚本会自动初始化）")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_git()
    
    if success:
        print("\n✓ Git已正确安装，可以继续部署")
        print("\n下一步:")
        print("1. 创建GitHub Personal Access Token（如果还没有）")
        print("   访问: https://github.com/settings/tokens")
        print("2. 创建GitHub仓库（如果还没有）")
        print("   访问: https://github.com/new")
        print("3. 运行部署脚本:")
        print("   双击: 部署到GitHub_Pages.bat")
    else:
        print("\n✗ Git未正确安装或配置")
        print("\n请:")
        print("1. 确认Git已安装")
        print("2. 关闭并重新打开PowerShell/命令提示符")
        print("3. 或重启电脑")
        print("4. 然后重新运行此测试脚本")
    
    input("\n按回车键退出...")

