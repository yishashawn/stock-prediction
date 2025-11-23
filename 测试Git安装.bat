@echo off
chcp 65001 >nul
echo ========================================
echo Git 安装测试
echo ========================================
echo.

REM 尝试查找Python解释器
set PYTHON_EXE=
if exist "C:\Users\syy\Python313\python.exe" set PYTHON_EXE=C:\Users\syy\Python313\python.exe
if not "%PYTHON_EXE%"=="" goto :found_python

for %%p in (C:\Python313 C:\Python312 C:\Python311 C:\Python310) do (
    if exist "%%p\python.exe" (
        set PYTHON_EXE="%%p\python.exe"
        goto :found_python
    )
)

where python >nul 2>&1
if not errorlevel 1 (
    set PYTHON_EXE=python
    goto :found_python
)

where py >nul 2>&1
if not errorlevel 1 (
    set PYTHON_EXE=py
    goto :found_python
)

:found_python
if "%PYTHON_EXE%"=="" (
    echo 错误: 未找到Python解释器。
    pause
    exit /b 1
)

echo 找到Python解释器: %PYTHON_EXE%
echo.
echo 正在测试Git安装...
echo.

%PYTHON_EXE% 测试Git安装.py

pause

