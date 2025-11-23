# Git安装 - 快速指南

## 🚀 推荐方法：一键安装

### 步骤1: 运行安装脚本

1. **找到文件**: `安装Git_简化版.bat`
2. **右键点击** → 选择 **"以管理员身份运行"**
3. **等待完成**: 脚本会自动下载并安装Git

### 步骤2: 重启终端

安装完成后：
- **关闭**当前所有PowerShell/命令提示符窗口
- **重新打开**新的PowerShell或命令提示符
- 或**重启电脑**（推荐）

### 步骤3: 验证安装

在新的PowerShell中运行：
```bash
git --version
```

如果显示版本号（如 `git version 2.43.0`），说明安装成功！

### 步骤4: 配置Git

运行以下命令配置用户信息：
```bash
git config --global user.email "435256553@qq.com"
git config --global user.name "syy"
```

验证配置：
```bash
git config --global --list
```

---

## 📥 备用方法：手动安装

如果自动安装失败，请查看：`手动安装Git指南.md`

### 快速手动安装步骤：

1. **下载Git**: https://git-scm.com/download/win
2. **运行安装程序**: 双击下载的 `.exe` 文件
3. **安装选项**: 使用默认选项，但注意选择：
   - ✅ "Git from the command line and also from 3rd-party software"
4. **完成安装**: 点击Next直到完成
5. **重启终端**: 关闭并重新打开PowerShell

---

## ✅ 安装后检查

运行以下命令检查：

```bash
# 检查Git版本
git --version

# 检查用户配置
git config --global --list

# 检查Git是否在PATH中
where git
```

---

## 🎯 下一步

安装并配置完成后：

1. **创建GitHub Personal Access Token**
   - 访问: https://github.com/settings/tokens
   - 创建新Token，权限选择 `repo`

2. **创建GitHub仓库**
   - 访问: https://github.com/new
   - 创建Public仓库

3. **运行部署脚本**
   - 双击: `部署到GitHub_Pages.bat`

---

## ❓ 常见问题

### Q: 提示"需要管理员权限"？

**A**: 右键点击安装脚本，选择"以管理员身份运行"

### Q: 下载很慢或失败？

**A**: 
- 检查网络连接
- 或手动下载: https://git-scm.com/download/win

### Q: 安装后仍提示"找不到git命令"？

**A**: 
- 关闭并重新打开所有PowerShell窗口
- 或重启电脑
- 检查PATH环境变量

### Q: 如何检查PATH环境变量？

**A**: 
1. 右键"此电脑" → 属性 → 高级系统设置 → 环境变量
2. 在"系统变量"中找到 `Path`
3. 检查是否包含 `C:\Program Files\Git\bin`

---

**现在开始：右键点击 `安装Git_简化版.bat` → "以管理员身份运行"** 🎯

