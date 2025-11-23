#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接配置Git环境
"""

import os
import subprocess
import sys
import platform

def find_git():
    """查找Git安装位置"""
    possible_paths = [
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files (x86)\Git\bin\git.exe",
        r"C:\Program Files (x86)\Git\cmd\git.exe",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # 尝试搜索
    git_dir = r"C:\Program Files\Git"
    if os.path.exists(git_dir):
        for root, dirs, files in os.walk(git_dir):
            if "git.exe" in files:
                return os.path.join(root, "git.exe")
    
    return None

def configure_git():
    """配置Git"""
    print("=" * 60)
    print("Git环境配置")
    print("=" * 60)
    print()
    
    # 查找Git
    print("步骤1: 查找Git安装位置...")
    git_exe = find_git()
    
    if not git_exe:
        print("✗ 未找到Git安装")
        print()
        print("请确认Git已正确安装，或运行: 安装Git_简化版.bat")
        return False
    
    print(f"✓ 找到Git: {git_exe}")
    print()
    
    # 测试Git
    print("步骤2: 测试Git...")
    try:
        result = subprocess.run([git_exe, "--version"], 
                               capture_output=True, 
                               text=True, 
                               timeout=5)
        if result.returncode == 0:
            print(f"✓ {result.stdout.strip()}")
        else:
            print("✗ Git无法运行")
            return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False
    print()
    
    # 配置用户信息
    print("步骤3: 配置Git用户信息...")
    try:
        subprocess.run([git_exe, "config", "--global", "user.email", "435256553@qq.com"],
                      check=True, timeout=5, capture_output=True)
        print("✓ 邮箱已配置: 435256553@qq.com")
        
        subprocess.run([git_exe, "config", "--global", "user.name", "syy"],
                      check=True, timeout=5, capture_output=True)
        print("✓ 用户名已配置: syy")
    except Exception as e:
        print(f"✗ 配置失败: {e}")
        return False
    print()
    
    # 验证配置
    print("步骤4: 验证配置...")
    try:
        result = subprocess.run([git_exe, "config", "--global", "--list"],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            user_lines = [l for l in lines if 'user' in l.lower()]
            for line in user_lines:
                print(f"  {line}")
    except:
        pass
    print()
    
    # 添加到PATH（需要管理员权限）
    print("步骤5: 配置PATH环境变量...")
    git_bin = os.path.dirname(git_exe)
    git_cmd = git_bin.replace("\\bin", "\\cmd")
    
    if not os.path.exists(git_cmd):
        git_cmd = None
    
    try:
        # 获取当前PATH
        machine_path = os.environ.get('Path', '')
        
        # 检查是否已在PATH中
        if git_bin in machine_path or (git_cmd and git_cmd in machine_path):
            print("✓ Git已在PATH中")
        else:
            print("⚠ Git未在PATH中")
            print()
            print("需要管理员权限才能修改系统PATH")
            print("请运行: 配置Git并添加到PATH.bat（以管理员身份运行）")
            print()
            print("或者手动添加以下路径到系统PATH:")
            print(f"  {git_bin}")
            if git_cmd:
                print(f"  {git_cmd}")
    except Exception as e:
        print(f"⚠ 检查PATH时出错: {e}")
    print()
    
    print("=" * 60)
    print("配置完成！")
    print("=" * 60)
    print()
    print("重要提示:")
    print("1. 如果Git未在PATH中，请:")
    print("   - 运行: 配置Git并添加到PATH.bat（以管理员身份运行）")
    print("   - 或重启电脑")
    print()
    print("2. 验证配置（在新的PowerShell中）:")
    print("   git --version")
    print("   git config --global --list")
    print()
    print("3. 下一步:")
    print("   - 创建GitHub Personal Access Token")
    print("   - 创建GitHub仓库")
    print("   - 运行: 部署到GitHub_Pages.bat")
    print()
    
    return True

if __name__ == "__main__":
    try:
        configure_git()
    except KeyboardInterrupt:
        print("\n\n已取消")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n按回车键退出...")

