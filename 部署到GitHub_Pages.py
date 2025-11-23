#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动部署中际旭创价格预测网站到GitHub Pages
"""

import os
import subprocess
import sys
import json

def check_git_installed():
    """检查Git是否已安装"""
    try:
        result = subprocess.run(['git', '--version'], 
                               capture_output=True, 
                               text=True, 
                               timeout=5)
        if result.returncode == 0:
            print(f"✓ Git已安装: {result.stdout.strip()}")
            return True
        else:
            return False
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"检查Git时出错: {e}")
        return False

def check_git_repo():
    """检查当前目录是否是Git仓库"""
    if os.path.exists('.git'):
        return True
    return False

def get_remote_url():
    """获取远程仓库URL"""
    try:
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'],
                               capture_output=True,
                               text=True,
                               timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except:
        return None

def init_git_repo():
    """初始化Git仓库"""
    print("\n正在初始化Git仓库...")
    try:
        subprocess.run(['git', 'init'], check=True, timeout=10)
        print("✓ Git仓库初始化成功")
        return True
    except subprocess.CalledProcessError:
        print("✗ Git仓库初始化失败")
        return False
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False

def create_gitignore():
    """创建.gitignore文件"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
*.egg-info/
dist/
build/

# 模型文件
models/
*.pkl
*.h5
*.pb

# 数据文件（可选，如果不想上传数据文件）
# *.csv
# *.json

# IDE
.vscode/
.idea/
*.swp
*.swo

# 系统文件
.DS_Store
Thumbs.db
"""
    try:
        with open('.gitignore', 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        print("✓ .gitignore文件已创建")
        return True
    except Exception as e:
        print(f"✗ 创建.gitignore失败: {e}")
        return False

def add_files():
    """添加需要上传的文件"""
    files_to_add = [
        '中际旭创_价格预测.html',
        '中际旭创_价格预测模型.png',
        '中际旭创_多因素散点图.png',
        '中际旭创_特征重要性详细分析.png',
        'index.html'
    ]
    
    # 查找所有散点图文件（可能有多个页面）
    scatter_plot_files = [f for f in os.listdir('.') if f.startswith('中际旭创_所有因素散点图_第') and f.endswith('.png')]
    files_to_add.extend(scatter_plot_files)
    
    # 检查文件是否存在
    existing_files = []
    missing_files = []
    
    for file in files_to_add:
        if os.path.exists(file):
            existing_files.append(file)
        else:
            missing_files.append(file)
    
    if missing_files:
        print(f"\n警告: 以下文件不存在，将跳过:")
        for f in missing_files:
            print(f"  - {f}")
    
    if not existing_files:
        print("\n✗ 没有找到需要上传的文件")
        return False
    
    print(f"\n找到 {len(existing_files)} 个文件，准备上传:")
    for f in existing_files:
        print(f"  ✓ {f}")
    
    try:
        # 配置Git以正确处理中文文件名
        subprocess.run(['git', 'config', '--global', 'core.quotepath', 'false'], 
                      capture_output=True, timeout=5)
        subprocess.run(['git', 'config', '--global', 'i18n.commitencoding', 'utf-8'], 
                      capture_output=True, timeout=5)
        
        # 使用Python的subprocess处理中文文件名，逐个添加文件
        for file in existing_files:
            try:
                # 使用绝对路径确保文件能被找到
                abs_path = os.path.abspath(file)
                subprocess.run(['git', 'add', abs_path], check=True, timeout=10, 
                             encoding='utf-8', errors='ignore')
            except subprocess.CalledProcessError as e:
                print(f"  警告: 添加文件失败 {file}: {e}")
                # 尝试使用相对路径
                try:
                    subprocess.run(['git', 'add', file], check=True, timeout=10,
                                 encoding='utf-8', errors='ignore')
                except:
                    print(f"  ✗ 无法添加: {file}")
        
        print("\n✓ 文件已添加到Git暂存区")
        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False

def commit_changes(message="更新预测数据"):
    """提交更改"""
    try:
        subprocess.run(['git', 'commit', '-m', message], 
                     check=True, 
                     timeout=10,
                     capture_output=True)
        print(f"✓ 更改已提交: {message}")
        return True
    except subprocess.CalledProcessError as e:
        if "nothing to commit" in e.stderr.decode('utf-8', errors='ignore'):
            print("ℹ 没有需要提交的更改")
            return True
        print(f"✗ 提交失败: {e.stderr.decode('utf-8', errors='ignore')}")
        return False
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False

def setup_remote(remote_url):
    """设置远程仓库"""
    try:
        # 检查是否已有远程仓库
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'],
                               capture_output=True,
                               text=True,
                               timeout=5)
        
        if result.returncode == 0:
            current_url = result.stdout.strip()
            if current_url == remote_url:
                print(f"✓ 远程仓库已设置: {remote_url}")
                return True
            else:
                print(f"当前远程仓库: {current_url}")
                print(f"目标远程仓库: {remote_url}")
                choice = input("是否更新远程仓库地址? (y/n): ").strip().lower()
                if choice == 'y':
                    subprocess.run(['git', 'remote', 'set-url', 'origin', remote_url], 
                                 check=True, timeout=5)
                    print(f"✓ 远程仓库已更新: {remote_url}")
                    return True
                else:
                    return False
        else:
            # 添加远程仓库
            subprocess.run(['git', 'remote', 'add', 'origin', remote_url], 
                         check=True, timeout=5)
            print(f"✓ 远程仓库已添加: {remote_url}")
            return True
    except subprocess.CalledProcessError:
        print("✗ 设置远程仓库失败")
        return False
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False

def push_to_github(branch='main'):
    """推送到GitHub"""
    try:
        # 检查分支是否存在
        result = subprocess.run(['git', 'branch', '--show-current'],
                               capture_output=True,
                               text=True,
                               timeout=5)
        current_branch = result.stdout.strip()
        
        if not current_branch:
            # 创建并切换到main分支
            subprocess.run(['git', 'branch', '-M', branch], check=True, timeout=5)
            print(f"✓ 已创建并切换到 {branch} 分支")
        else:
            if current_branch != branch:
                subprocess.run(['git', 'branch', '-M', branch], check=True, timeout=5)
                print(f"✓ 已切换到 {branch} 分支")
        
        # 推送
        print(f"\n正在推送到GitHub...")
        subprocess.run(['git', 'push', '-u', 'origin', branch], 
                     check=True, 
                     timeout=30)
        print(f"✓ 已成功推送到GitHub")
        return True
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)
        if "fatal: not a git repository" in error_msg:
            print("✗ 当前目录不是Git仓库，请先初始化")
        elif "fatal: could not read Username" in error_msg or "Authentication failed" in error_msg:
            print("\n✗ 身份验证失败")
            print("\n解决方法:")
            print("1. 使用GitHub Personal Access Token (推荐)")
            print("   - 访问: https://github.com/settings/tokens")
            print("   - 生成新token，权限选择 'repo'")
            print("   - 使用token作为密码")
            print("\n2. 或使用SSH密钥")
            print("   - 生成SSH密钥: ssh-keygen -t ed25519 -C 'your_email@example.com'")
            print("   - 添加到GitHub: https://github.com/settings/keys")
            print("   - 使用SSH URL: git@github.com:用户名/仓库名.git")
        else:
            print(f"✗ 推送失败: {error_msg}")
        return False
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False

def create_index_html():
    """创建index.html，自动跳转到预测页面"""
    index_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="0; url=中际旭创_价格预测.html">
    <title>中际旭创股票价格预测</title>
    <style>
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            text-align: center;
        }
        h1 {
            font-size: 2.5em;
            margin-bottom: 20px;
        }
        p {
            font-size: 1.2em;
            margin: 10px 0;
        }
        a {
            color: #fff;
            text-decoration: underline;
            font-weight: bold;
        }
        .spinner {
            border: 4px solid rgba(255, 255, 255, 0.3);
            border-top: 4px solid white;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>中际旭创股票价格预测</h1>
        <div class="spinner"></div>
        <p>正在跳转到预测页面...</p>
        <p>如果未自动跳转，请<a href="中际旭创_价格预测.html">点击这里</a></p>
    </div>
</body>
</html>
"""
    try:
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(index_content)
        print("✓ index.html已创建（自动跳转页面）")
        return True
    except Exception as e:
        print(f"✗ 创建index.html失败: {e}")
        return False

def main():
    print("=" * 60)
    print("GitHub Pages 自动部署工具")
    print("=" * 60)
    
    # 配置Git以正确处理中文
    try:
        subprocess.run(['git', 'config', '--global', 'core.quotepath', 'false'], 
                      capture_output=True, timeout=5)
        subprocess.run(['git', 'config', '--global', 'i18n.commitencoding', 'utf-8'], 
                      capture_output=True, timeout=5)
    except:
        pass  # 如果配置失败，继续执行
    
    # 检查Git
    if not check_git_installed():
        print("\n✗ Git未安装")
        print("\n请先安装Git:")
        print("1. 运行: 安装Git_简化版.bat")
        print("2. 或访问: https://git-scm.com/download/win")
        print("3. 安装完成后重新运行此脚本")
        input("\n按回车键退出...")
        return
    
    # 检查是否在项目目录
    if not os.path.exists('中际旭创_价格预测.html'):
        print("\n✗ 找不到 中际旭创_价格预测.html")
        print("请先运行: 运行预测模型.bat 生成HTML文件")
        input("\n按回车键退出...")
        return
    
    # 检查Git仓库
    is_repo = check_git_repo()
    remote_url = get_remote_url()
    
    if not is_repo:
        print("\n当前目录不是Git仓库")
        choice = input("是否初始化Git仓库? (y/n): ").strip().lower()
        if choice != 'y':
            print("已取消")
            return
        if not init_git_repo():
            return
        create_gitignore()
    else:
        print(f"\n✓ 当前目录是Git仓库")
        if remote_url:
            print(f"✓ 远程仓库: {remote_url}")
        else:
            print("ℹ 未设置远程仓库")
    
    # 创建index.html
    if not os.path.exists('index.html'):
        create_index_html()
    
    # 获取远程仓库URL
    if not remote_url:
        print("\n" + "=" * 60)
        print("请提供GitHub仓库URL")
        print("=" * 60)
        print("\n格式示例:")
        print("  HTTPS: https://github.com/用户名/仓库名.git")
        print("  SSH:   git@github.com:用户名/仓库名.git")
        print("\n如果没有仓库，请先:")
        print("1. 访问 https://github.com/new")
        print("2. 创建新仓库（选择Public）")
        print("3. 复制仓库URL")
        print("=" * 60)
        remote_url = input("\n请输入GitHub仓库URL: ").strip()
        
        if not remote_url:
            print("已取消")
            return
        
        if not remote_url.startswith('http') and not remote_url.startswith('git@'):
            print("✗ URL格式不正确")
            return
    
    # 设置远程仓库
    if not setup_remote(remote_url):
        return
    
    # 添加文件
    if not add_files():
        return
    
    # 提交
    commit_msg = input("\n请输入提交信息（直接回车使用默认）: ").strip()
    if not commit_msg:
        commit_msg = "更新中际旭创股票价格预测数据"
    
    if not commit_changes(commit_msg):
        return
    
    # 推送
    print("\n" + "=" * 60)
    print("准备推送到GitHub")
    print("=" * 60)
    print("\n注意:")
    print("- 如果是第一次推送，可能需要输入GitHub用户名和密码")
    print("- ⚠️ 重要: 密码请使用Personal Access Token（不是GitHub密码）")
    print("- GitHub已不支持使用密码进行Git操作")
    print("- 生成Token: https://github.com/settings/tokens")
    print("- 详细步骤请查看: 创建GitHub_Token指南.md")
    print("\n当提示输入凭据时:")
    print("  用户名: 您的GitHub邮箱或用户名")
    print("  密码: 粘贴Personal Access Token（不是GitHub密码）")
    print("=" * 60)
    
    choice = input("\n是否继续推送? (y/n): ").strip().lower()
    if choice != 'y':
        print("已取消")
        return
    
    if push_to_github():
        print("\n" + "=" * 60)
        print("部署成功！")
        print("=" * 60)
        
        # 从远程URL提取用户名和仓库名
        if 'github.com' in remote_url:
            parts = remote_url.replace('.git', '').split('/')
            if len(parts) >= 2:
                username = parts[-2] if parts[-2] != 'github.com' else parts[-1]
                repo_name = parts[-1]
                pages_url = f"https://{username}.github.io/{repo_name}/"
                print(f"\n您的网站地址:")
                print(f"  主页: {pages_url}")
                print(f"  预测页面: {pages_url}中际旭创_价格预测.html")
                print(f"\n注意: GitHub Pages可能需要几分钟才能生效")
                print(f"如果无法访问，请检查:")
                print(f"1. 仓库设置 → Pages → Source 是否设置为 'main' 分支")
                print(f"2. 仓库是否为 'Public'（公开仓库才能使用免费版GitHub Pages）")
        
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("部署失败，请查看上面的错误信息")
        print("=" * 60)
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()

