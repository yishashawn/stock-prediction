@echo off
chcp 65001 >nul
title Git诊断和修复工具
color 0E

echo.
echo ========================================
echo Git诊断和修复工具
echo ========================================
echo.

echo [诊断] 检查Git安装状态...
echo.

REM 检查目录
if exist "C:\Program Files\Git" (
    echo [OK] Git目录存在: C:\Program Files\Git
    echo.
    echo [信息] 正在搜索git.exe文件...
    echo.
    
    REM 搜索git.exe
    set FOUND=0
    set GIT_EXE=
    
    if exist "C:\Program Files\Git\bin\git.exe" (
        echo [OK] 找到: C:\Program Files\Git\bin\git.exe
        set "GIT_EXE=C:\Program Files\Git\bin\git.exe"
        set FOUND=1
    )
    
    if exist "C:\Program Files\Git\cmd\git.exe" (
        echo [OK] 找到: C:\Program Files\Git\cmd\git.exe
        set "GIT_EXE=C:\Program Files\Git\cmd\git.exe"
        set FOUND=1
    )
    
    if exist "C:\Program Files\Git\usr\bin\git.exe" (
        echo [OK] 找到: C:\Program Files\Git\usr\bin\git.exe
        set "GIT_EXE=C:\Program Files\Git\usr\bin\git.exe"
        set FOUND=1
    )
    
    if %FOUND%==0 (
        echo [错误] 未找到git.exe文件
        echo.
        echo [建议] Git可能安装不完整
        echo [操作] 建议重新安装Git
        echo.
        echo 请运行: 安装Git_简化版.bat
        echo.
        pause
        exit /b 1
    )
    
    echo.
    echo [测试] 测试Git是否可用...
    "%GIT_EXE%" --version
    if errorlevel 1 (
        echo [错误] Git无法运行
        pause
        exit /b 1
    )
    
    echo.
    echo [配置] 配置Git用户信息...
    "%GIT_EXE%" config --global user.email "435256553@qq.com"
    if errorlevel 1 (
        echo [警告] 配置邮箱失败
    ) else (
        echo [OK] 邮箱已配置
    )
    
    "%GIT_EXE%" config --global user.name "syy"
    if errorlevel 1 (
        echo [警告] 配置用户名失败
    ) else (
        echo [OK] 用户名已配置
    )
    
    echo.
    echo [验证] 验证配置...
    "%GIT_EXE%" config --global --list | findstr "user"
    
    echo.
    echo ========================================
    echo Git配置完成！
    echo ========================================
    echo.
    echo Git位置: %GIT_EXE%
    echo.
    echo 重要: 如果git命令仍无法使用，请:
    echo   1. 运行: 配置Git并添加到PATH.bat（以管理员身份运行）
    echo   2. 或重启电脑
    echo.
    echo 下一步:
    echo   1. 创建GitHub Personal Access Token
    echo   2. 创建GitHub仓库
    echo   3. 运行: 部署到GitHub_Pages.bat
    echo.
    
) else (
    echo [错误] Git目录不存在
    echo.
    echo [建议] 请先安装Git
    echo [操作] 运行: 安装Git_简化版.bat
    echo.
)

echo.
echo 按任意键退出...
pause >nul
