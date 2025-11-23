# -*- coding: utf-8 -*-
import os
import subprocess

print("=" * 60)
print("Git安装检查")
print("=" * 60)
print()

git_dir = r"C:\Program Files\Git"
if os.path.exists(git_dir):
    print(f"✓ Git目录存在: {git_dir}")
    print()
    
    # 查找git.exe
    possible_locations = [
        os.path.join(git_dir, "bin", "git.exe"),
        os.path.join(git_dir, "cmd", "git.exe"),
        os.path.join(git_dir, "usr", "bin", "git.exe"),
    ]
    
    git_exe = None
    for path in possible_locations:
        if os.path.exists(path):
            print(f"✓ 找到git.exe: {path}")
            git_exe = path
            break
    
    if not git_exe:
        print("✗ 未找到git.exe")
        print()
        print("可能的原因:")
        print("1. Git安装不完整")
        print("2. git.exe在其他位置")
        print()
        print("建议: 运行 安装Git_简化版.bat 重新安装")
    else:
        print()
        print("测试Git...")
        try:
            result = subprocess.run([git_exe, "--version"], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                print(f"✓ {result.stdout.strip()}")
                print()
                
                print("配置Git用户信息...")
                subprocess.run([git_exe, "config", "--global", "user.email", "435256553@qq.com"],
                             timeout=5, capture_output=True)
                subprocess.run([git_exe, "config", "--global", "user.name", "syy"],
                             timeout=5, capture_output=True)
                print("✓ 用户信息已配置")
                print()
                
                print("验证配置:")
                result = subprocess.run([git_exe, "config", "--global", "--list"],
                                      capture_output=True, text=True, timeout=5)
                for line in result.stdout.strip().split('\n'):
                    if 'user' in line.lower():
                        print(f"  {line}")
                
                print()
                print("=" * 60)
                print("配置完成！")
                print("=" * 60)
                print()
                print("如果git命令仍无法使用，请:")
                print("1. 运行: 配置Git并添加到PATH.bat（以管理员身份运行）")
                print("2. 或重启电脑")
            else:
                print("✗ Git无法运行")
        except Exception as e:
            print(f"✗ 测试失败: {e}")
else:
    print("✗ Git目录不存在")
    print()
    print("请运行: 安装Git_简化版.bat")

print()
input("按回车键退出...")

