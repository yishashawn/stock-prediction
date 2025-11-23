@echo off
chcp 65001 >nul
title Deploy to GitHub Pages
color 0A

echo.
echo ========================================
echo Deploy to GitHub Pages
echo ========================================
echo.

REM Add Git to PATH
set "PATH=%PATH%;C:\Program Files\Git\bin;C:\Program Files\Git\cmd"

REM Check Git
where git >nul 2>&1
if %errorLevel% neq 0 (
    echo [Error] Git not in PATH
    echo Please run: 添加Git到PATH.bat (as administrator)
    echo.
    pause
    exit /b 1
)

echo [OK] Git is available
git --version
echo.

REM Check Python
set PYTHON_EXE=
if exist "C:\Users\syy\Python313\python.exe" (
    set PYTHON_EXE=C:\Users\syy\Python313\python.exe
) else (
    where python >nul 2>&1
    if %errorLevel% equ 0 (
        set PYTHON_EXE=python
    ) else (
        echo [Error] Python not found
        pause
        exit /b 1
    )
)

echo [OK] Python found: %PYTHON_EXE%
echo.

REM Run deployment script
echo [Info] Starting deployment script...
echo.

"%PYTHON_EXE%" "部署到GitHub_Pages.py"

echo.
pause

