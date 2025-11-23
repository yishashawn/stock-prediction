@echo off
chcp 65001 >nul
title Deploy to GitHub
color 0A

set "PATH=%PATH%;C:\Program Files\Git\bin;C:\Program Files\Git\cmd"

echo.
echo Starting deployment...
echo.

C:\Users\syy\Python313\python.exe "部署到GitHub_Pages.py"

pause

