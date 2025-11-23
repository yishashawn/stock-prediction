@echo off
chcp 65001 >nul
echo ========================================
echo 中际旭创股票价格预测模型
echo ========================================
echo.

REM 设置Python路径变量
set PYTHON_PATH=

REM 检查常见的Python路径
if exist "C:\Users\syy\Python313\python.exe" (
    set PYTHON_PATH=C:\Users\syy\Python313\python.exe
    echo 找到Python: %PYTHON_PATH%
    goto :found_python
)

if exist "C:\Python313\python.exe" (
    set PYTHON_PATH=C:\Python313\python.exe
    echo 找到Python: %PYTHON_PATH%
    goto :found_python
)

if exist "C:\Python312\python.exe" (
    set PYTHON_PATH=C:\Python312\python.exe
    echo 找到Python: %PYTHON_PATH%
    goto :found_python
)

if exist "C:\Python311\python.exe" (
    set PYTHON_PATH=C:\Python311\python.exe
    echo 找到Python: %PYTHON_PATH%
    goto :found_python
)

if exist "C:\Python310\python.exe" (
    set PYTHON_PATH=C:\Python310\python.exe
    echo 找到Python: %PYTHON_PATH%
    goto :found_python
)

REM 检查系统PATH中的Python
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_PATH=python
    echo 找到Python: python (系统PATH)
    goto :found_python
)

py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_PATH=py
    echo 找到Python: py (Python启动器)
    goto :found_python
)

REM 如果都没找到，尝试搜索常见位置
echo 正在搜索Python安装位置...
for /d %%i in (C:\Users\*\Python*) do (
    if exist "%%i\python.exe" (
        set PYTHON_PATH=%%i\python.exe
        echo 找到Python: %PYTHON_PATH%
        goto :found_python
    )
)

for /d %%i in (C:\Python*) do (
    if exist "%%i\python.exe" (
        set PYTHON_PATH=%%i\python.exe
        echo 找到Python: %PYTHON_PATH%
        goto :found_python
    )
)

REM 如果还是没找到，显示错误信息
echo.
echo ========================================
echo 错误: 未找到Python
echo ========================================
echo.
echo 请选择以下方式之一：
echo 1. 安装Python并添加到系统PATH
echo 2. 将Python路径添加到系统环境变量
echo 3. 手动修改此批处理文件，设置PYTHON_PATH变量
echo.
echo 如果Python已安装但未找到，请：
echo - 检查Python是否安装在: C:\Users\syy\Python313
echo - 或修改此批处理文件中的PYTHON_PATH变量
echo.
pause
exit /b 1

:found_python
echo.
echo ========================================
echo 使用Python: %PYTHON_PATH%
echo ========================================
echo.

REM 检查并安装依赖
echo 正在检查依赖包...
%PYTHON_PATH% -m pip install -q --no-warn-script-location -r requirements.txt
if errorlevel 1 (
    echo 警告: 依赖包安装可能有问题，但继续运行...
)

REM 运行预测脚本
echo.
echo 正在运行预测模型...
echo.
%PYTHON_PATH% predict_stock_price_advanced.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo 运行出错！
    echo ========================================
    echo.
    echo 请检查上面的错误信息
    pause
    exit /b 1
)

echo.
echo ========================================
echo 运行完成！
echo ========================================
pause

