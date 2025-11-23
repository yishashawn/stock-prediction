# Git安装步骤 - 快速指南

## 📥 您的情况

您已经有Git安装程序在：
`C:\工作\项目\13-github\Git-2.49.0-64-bit.exe`

## 🚀 安装步骤

### 方法1: 使用脚本安装（推荐）

1. **双击运行**: `install_git.bat`
2. **安装程序会弹出**，按照提示完成安装
3. **重要**: 在"Adjusting your PATH environment"步骤，选择：
   - ✅ **"Git from the command line and also from 3rd-party software"**
4. **其他选项**: 使用默认设置即可
5. **完成安装**: 点击Next直到完成

### 方法2: 手动安装

1. **找到安装程序**: `C:\工作\项目\13-github\Git-2.49.0-64-bit.exe`
2. **双击运行**安装程序
3. **按照提示完成安装**，注意选择PATH选项

## ✅ 安装后检查

安装完成后，运行：`检查Git安装状态.bat`

或者手动检查：
```bash
"C:\Program Files\Git\bin\git.exe" --version
```

## 🔧 配置Git

安装完成后，运行：`配置Git并添加到PATH.bat`（以管理员身份运行）

这会：
1. 将Git添加到PATH环境变量
2. 配置用户信息（邮箱和用户名）

## ⚠️ 重要提示

1. **重启终端**: 安装和配置完成后，请关闭并重新打开所有PowerShell/命令提示符窗口
2. **或重启电脑**: 最可靠的方法
3. **验证**: 在新的PowerShell中运行 `git --version`

## 🎯 下一步

配置完成后：
1. 创建GitHub Personal Access Token
2. 创建GitHub仓库
3. 运行部署脚本

---

**现在开始：双击运行 `install_git.bat` 开始安装！** 🎉

