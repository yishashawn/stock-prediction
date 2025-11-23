# Git自动安装脚本
# 需要管理员权限运行

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Green
Write-Host "Git for Windows 自动安装工具" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "警告: 需要管理员权限来安装Git" -ForegroundColor Yellow
    Write-Host "请右键点击此脚本，选择'以管理员身份运行'" -ForegroundColor Yellow
    Write-Host ""
    $choice = Read-Host "是否现在以管理员身份重新运行? (y/n)"
    if ($choice -eq 'y') {
        Start-Process powershell.exe -Verb RunAs -ArgumentList "-File `"$PSCommandPath`""
        exit
    } else {
        Write-Host "已取消安装"
        Read-Host "按回车键退出"
        exit
    }
}

# Git下载URL（官方最新版本）
$gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe"
$installerPath = "$env:TEMP\GitInstaller.exe"

Write-Host "步骤1: 下载Git安装程序..." -ForegroundColor Cyan
Write-Host "下载地址: $gitUrl" -ForegroundColor Gray
Write-Host "保存路径: $installerPath" -ForegroundColor Gray
Write-Host ""

try {
    # 下载Git安装程序
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $gitUrl -OutFile $installerPath -UseBasicParsing
    Write-Host "✓ 下载完成" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "✗ 下载失败: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "请手动下载Git:" -ForegroundColor Yellow
    Write-Host "1. 访问: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "2. 下载并运行安装程序" -ForegroundColor Yellow
    Read-Host "按回车键退出"
    exit 1
}

Write-Host "步骤2: 安装Git..." -ForegroundColor Cyan
Write-Host "注意: 安装程序会弹出窗口，请按照提示完成安装" -ForegroundColor Yellow
Write-Host ""

# 静默安装参数
# /SILENT - 静默安装
# /NORESTART - 不重启
# /DIR - 安装目录
$installArgs = "/SILENT /NORESTART /DIR=`"C:\Program Files\Git`""

try {
    Write-Host "正在启动安装程序..." -ForegroundColor Cyan
    Start-Process -FilePath $installerPath -ArgumentList $installArgs -Wait
    
    Write-Host ""
    Write-Host "✓ Git安装完成！" -ForegroundColor Green
    Write-Host ""
    
    # 添加到PATH（如果还没有）
    $gitPath = "C:\Program Files\Git\bin"
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    
    if ($currentPath -notlike "*$gitPath*") {
        Write-Host "步骤3: 添加到PATH环境变量..." -ForegroundColor Cyan
        $newPath = $currentPath + ";" + $gitPath
        [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
        Write-Host "✓ 已添加到PATH" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host "✓ Git已在PATH中" -ForegroundColor Green
        Write-Host ""
    }
    
    # 清理安装程序
    Remove-Item $installerPath -ErrorAction SilentlyContinue
    
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "安装完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "重要提示:" -ForegroundColor Yellow
    Write-Host "1. 请关闭并重新打开PowerShell/命令提示符" -ForegroundColor Yellow
    Write-Host "2. 或重启电脑（推荐）" -ForegroundColor Yellow
    Write-Host "3. 然后运行 'git --version' 验证安装" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "下一步:" -ForegroundColor Cyan
    Write-Host "1. 配置Git用户信息:" -ForegroundColor White
    Write-Host "   git config --global user.email `"435256553@qq.com`"" -ForegroundColor Gray
    Write-Host "   git config --global user.name `"syy`"" -ForegroundColor Gray
    Write-Host "2. 创建GitHub Personal Access Token" -ForegroundColor White
    Write-Host "3. 运行部署脚本: 部署到GitHub_Pages.bat" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host "✗ 安装失败: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "请手动安装Git:" -ForegroundColor Yellow
    Write-Host "1. 访问: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "2. 下载并运行安装程序" -ForegroundColor Yellow
    Write-Host "3. 使用默认安装选项" -ForegroundColor Yellow
}

Read-Host "按回车键退出"

