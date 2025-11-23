@echo off
chcp 65001 >nul
echo ========================================
echo 中际旭创股票价格预测 - Web服务器
echo ========================================
echo.

REM 尝试查找Python解释器
set PYTHON_EXE=
REM 优先使用用户指定的Python路径
if exist "C:\Users\syy\Python313\python.exe" set PYTHON_EXE=C:\Users\syy\Python313\python.exe
if not "%PYTHON_EXE%"=="" goto :found_python

REM 尝试常见Python安装路径
for %%p in (C:\Python313 C:\Python312 C:\Python311 C:\Python310) do (
    if exist "%%p\python.exe" (
        set PYTHON_EXE="%%p\python.exe"
        goto :found_python
    )
)

REM 尝试在PATH中查找python命令
where python >nul 2>&1
if not errorlevel 1 (
    set PYTHON_EXE=python
    goto :found_python
)

REM 尝试使用py启动器
where py >nul 2>&1
if not errorlevel 1 (
    set PYTHON_EXE=py
    goto :found_python
)

:found_python
if "%PYTHON_EXE%"=="" (
    echo 错误: 未找到Python解释器。
    echo 请确保Python已安装。
    pause
    exit /b 1
) else (
    echo 找到Python解释器: %PYTHON_EXE%
)

echo.
echo 正在启动Web服务器...
echo.

REM 运行Python脚本
%PYTHON_EXE% 启动Web服务器.py

pause

