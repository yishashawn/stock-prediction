# 中际旭创股票价格预测模型 - PowerShell启动脚本
# 设置编码为UTF-8
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================" -ForegroundColor Green
Write-Host "中际旭创股票价格预测模型" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 检查Python是否安装
$pythonPath = $null

# 检查常见的Python路径
$possiblePaths = @(
    "C:\Users\syy\Python313\python.exe",
    "C:\Python313\python.exe",
    "C:\Python312\python.exe",
    "C:\Python311\python.exe",
    "C:\Python310\python.exe"
)

foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $pythonPath = $path
        Write-Host "找到Python: $pythonPath" -ForegroundColor Green
        break
    }
}

# 如果没找到，检查系统PATH
if (-not $pythonPath) {
    try {
        $version = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonPath = "python"
            Write-Host "找到Python: python (系统PATH)" -ForegroundColor Green
        }
    } catch {
        # 继续检查
    }
}

# 如果还是没找到，尝试py启动器
if (-not $pythonPath) {
    try {
        $version = py --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonPath = "py"
            Write-Host "找到Python: py (Python启动器)" -ForegroundColor Green
        }
    } catch {
        # 继续检查
    }
}

# 如果还是没找到，搜索常见位置
if (-not $pythonPath) {
    Write-Host "正在搜索Python安装位置..." -ForegroundColor Yellow
    $searchPaths = @(
        "$env:USERPROFILE\Python*",
        "C:\Python*"
    )
    
    foreach ($searchPath in $searchPaths) {
        $found = Get-ChildItem -Path $searchPath -Filter "python.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) {
            $pythonPath = $found.FullName
            Write-Host "找到Python: $pythonPath" -ForegroundColor Green
            break
        }
    }
}

# 如果还是没找到，显示错误
if (-not $pythonPath) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "错误: 未找到Python" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "请选择以下方式之一：" -ForegroundColor Yellow
    Write-Host "1. 安装Python并添加到系统PATH"
    Write-Host "2. 将Python路径添加到系统环境变量"
    Write-Host "3. 手动修改此PowerShell脚本，设置`$pythonPath变量"
    Write-Host ""
    Write-Host "如果Python已安装但未找到，请：" -ForegroundColor Yellow
    Write-Host "- 检查Python是否安装在: C:\Users\syy\Python313"
    Write-Host "- 或修改此脚本中的`$pythonPath变量"
    Write-Host ""
    Read-Host "按Enter键退出"
    exit 1
}

Write-Host "Python版本: " -NoNewline
& $pythonPath --version
Write-Host ""

# 检查并安装依赖
Write-Host "正在检查依赖包..." -ForegroundColor Yellow
& $pythonPath -m pip install -q --no-warn-script-location -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "警告: 依赖包安装可能有问题，但继续运行..." -ForegroundColor Yellow
}

# 运行预测脚本
Write-Host ""
Write-Host "正在运行预测模型..." -ForegroundColor Yellow
Write-Host ""
& $pythonPath predict_stock_price_advanced.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "运行出错！" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "请检查上面的错误信息" -ForegroundColor Yellow
    Read-Host "按Enter键退出"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "运行完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Read-Host "按Enter键退出"

