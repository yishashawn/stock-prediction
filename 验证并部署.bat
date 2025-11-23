@echo off
chcp 65001 >nul
title 验证GitHub仓库并部署
color 0B

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║        验证GitHub仓库并完成部署                         ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

REM 检查Git
where git >nul 2>&1
if errorlevel 1 (
    echo [错误] Git未安装
    pause
    exit /b 1
)

echo [步骤1] 检查远程仓库配置...
git remote -v
echo.

echo [步骤2] 检查仓库是否存在...
echo 正在验证: https://github.com/yishashawn/zhongji
echo.

REM 尝试访问仓库（通过git ls-remote）
echo 提示: 如果仓库不存在，会显示错误信息
echo 如果仓库存在但需要认证，会提示输入用户名和Token
echo.
pause

git ls-remote https://github.com/yishashawn/zhongji.git 2>&1
if errorlevel 1 (
    echo.
    echo ═══════════════════════════════════════════════════════════
    echo [警告] 仓库可能不存在或无法访问
    echo ═══════════════════════════════════════════════════════════
    echo.
    echo 请选择:
    echo 1. 如果仓库不存在，请先创建:
    echo    - 访问: https://github.com/new
    echo    - 仓库名: zhongji
    echo    - 选择: Public
    echo    - 创建后重新运行此脚本
    echo.
    echo 2. 如果仓库存在，可能是认证问题
    echo    - 检查Token是否正确
    echo    - 确认Token权限包含 'repo'
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo [OK] 仓库存在且可访问
    echo.
)

echo [步骤3] 准备部署文件...
echo.

REM 检查HTML文件
if not exist "中际旭创_价格预测.html" (
    echo [警告] 未找到HTML文件
    echo 请先运行: 运行预测模型.bat
    pause
    exit /b 1
)

echo [OK] HTML文件存在
echo.

echo [步骤4] 添加文件到Git...
git add 中际旭创_价格预测.html 2>nul
git add 中际旭创_价格预测模型.png 2>nul
git add 中际旭创_多因素散点图.png 2>nul
git add 中际旭创_特征重要性详细分析.png 2>nul
git add index.html 2>nul
git add 中际旭创_所有因素散点图_*.png 2>nul

echo [OK] 文件已添加
echo.

echo [步骤5] 提交更改...
git commit -m "更新中际旭创股票价格预测数据" 2>&1
if errorlevel 1 (
    echo [信息] 可能没有需要提交的更改，或已提交
)
echo.

echo [步骤6] 推送到GitHub...
echo.
echo ⚠️ 重要提示:
echo - 当提示输入用户名: 输入 435256553@qq.com
echo - 当提示输入密码: 粘贴您的Token（不是GitHub密码）
echo - Token: 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
echo.
pause

git push -u origin main
if errorlevel 1 (
    echo.
    echo [错误] 推送失败
    echo 请检查:
    echo 1. 仓库是否存在
    echo 2. Token是否正确
    echo 3. Token权限是否包含 'repo'
    pause
    exit /b 1
) else (
    echo.
    echo ═══════════════════════════════════════════════════════════
    echo [成功] 部署完成！
    echo ═══════════════════════════════════════════════════════════
    echo.
    echo 您的网站地址:
    echo https://yishashawn.github.io/zhongji/
    echo.
    echo 注意: 需要启用GitHub Pages:
    echo 1. 访问: https://github.com/yishashawn/zhongji/settings/pages
    echo 2. Source: 选择 main 和 / (root)
    echo 3. Save
    echo 4. 等待1-5分钟生效
    echo.
)

pause

