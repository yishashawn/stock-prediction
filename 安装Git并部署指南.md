# 安装Git并部署到GitHub Pages - 完整指南

## 📋 步骤概览

1. ✅ 安装Git
2. ✅ 创建GitHub Personal Access Token
3. ✅ 创建GitHub仓库
4. ✅ 运行部署脚本

---

## 步骤1: 安装Git

### 下载Git for Windows

1. **访问下载页面**: https://git-scm.com/download/win
2. **下载安装程序**: 点击下载按钮（会自动检测64位或32位）
3. **运行安装程序**: 双击下载的 `.exe` 文件

### 安装选项（推荐设置）

安装过程中，建议选择以下选项：

1. **选择组件**:
   - ✅ Git Bash Here
   - ✅ Git GUI Here
   - ✅ Associate .git* configuration files with the default text editor
   - ✅ Associate .sh files to be run with Bash

2. **选择默认编辑器**: 选择您喜欢的编辑器（如Notepad++或VS Code）

3. **调整PATH环境**:
   - ✅ 选择 "Git from the command line and also from 3rd-party software"（推荐）

4. **其他选项**: 使用默认设置即可

5. **完成安装**: 点击 "Install"

### 验证安装

安装完成后，打开新的命令提示符或PowerShell，运行：

```bash
git --version
```

如果显示版本号（如 `git version 2.xx.x`），说明安装成功。

---

## 步骤2: 创建GitHub Personal Access Token

⚠️ **重要**: GitHub从2021年8月起不再支持使用密码进行Git操作，必须使用Token。

### 详细步骤

1. **登录GitHub**:
   - 访问: https://github.com/login
   - 使用您的账号: **435256553@qq.com**
   - 密码: **jjjydxm6**

2. **访问Token设置**:
   - 直接访问: https://github.com/settings/tokens
   - 或: 点击右上角头像 → Settings → 左侧菜单最下方 "Developer settings" → "Personal access tokens" → "Tokens (classic)"

3. **生成新Token**:
   - 点击 "Generate new token" → 选择 "Generate new token (classic)"
   - 如果提示输入密码，请输入: **jjjydxm6**

4. **设置Token**:
   - **Note（备注）**: `GitHub Pages 部署`
   - **Expiration（过期时间）**: 选择 "90 days" 或 "No expiration"
   - **Select scopes（权限）**: 
     - ✅ **必须勾选**: `repo`（完整仓库权限）
     - ✅ 可选: `workflow`（如果需要GitHub Actions）

5. **生成并复制Token**:
   - 滚动到底部，点击 "Generate token"（绿色按钮）
   - ⚠️ **重要**: Token只显示一次，立即复制并保存
   - Token格式类似: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

6. **保存Token**: 将Token保存在安全的地方（密码管理器或本地文件）

---

## 步骤3: 创建GitHub仓库

1. **访问创建页面**: https://github.com/new

2. **填写仓库信息**:
   - **Repository name**: `stock-prediction`（或您喜欢的名称）
   - **Description**: `中际旭创股票价格预测网站`（可选）
   - **Visibility**: ✅ 选择 **Public**（公开，才能使用免费GitHub Pages）
   - ❌ **不要**勾选 "Add a README file"（脚本会自动处理）
   - ❌ **不要**勾选 "Add .gitignore" 和 "Choose a license"

3. **创建仓库**: 点击 "Create repository"（绿色按钮）

4. **复制仓库URL**: 
   - 创建后会显示仓库页面
   - 点击绿色的 "Code" 按钮
   - 复制HTTPS URL，例如: `https://github.com/您的用户名/stock-prediction.git`

---

## 步骤4: 配置Git（首次使用）

打开命令提示符或PowerShell，运行：

```bash
git config --global user.email "435256553@qq.com"
git config --global user.name "您的GitHub用户名"
```

---

## 步骤5: 运行部署脚本

1. **双击运行**: `部署到GitHub_Pages.bat`

2. **按提示操作**:
   - 脚本会检查Git是否安装
   - 如果是第一次，会初始化Git仓库
   - 输入GitHub仓库URL（步骤3中复制的）
   - 输入提交信息（或直接回车使用默认）

3. **输入凭据**（当提示时）:
   - **Username（用户名）**: `435256553@qq.com`（或您的GitHub用户名）
   - **Password（密码）**: 粘贴步骤2中创建的Personal Access Token（不是GitHub密码）

4. **等待推送完成**: 脚本会自动上传文件到GitHub

---

## 步骤6: 启用GitHub Pages

1. **打开仓库页面**: https://github.com/您的用户名/stock-prediction

2. **进入设置**:
   - 点击仓库页面顶部的 "Settings"（设置）标签

3. **启用Pages**:
   - 在左侧菜单中找到 "Pages"
   - 在 "Source" 部分：
     - **Branch**: 选择 `main`
     - **Folder**: 选择 `/ (root)`
   - 点击 "Save"（保存）

4. **等待生效**:
   - GitHub会显示您的网站地址
   - 通常需要1-2分钟才能访问

---

## 步骤7: 访问网站

您的网站地址：
- **主页**: `https://您的用户名.github.io/stock-prediction/`
- **预测页面**: `https://您的用户名.github.io/stock-prediction/中际旭创_价格预测.html`

---

## 🔄 更新网站

每次运行预测模型后，更新网站：

1. 运行 `predict_stock_price_advanced.py` 生成新的HTML
2. 运行 `部署到GitHub_Pages.bat`
3. 输入提交信息（如：`更新预测数据`）
4. 输入Token（Git会记住，之后可能不需要再输入）

---

## ❓ 常见问题

### Q: Git安装后仍然提示"找不到git命令"？

**A**: 
- 关闭并重新打开命令提示符/PowerShell
- 或重启电脑
- 检查Git是否添加到PATH环境变量

### Q: 推送时提示"Authentication failed"？

**A**: 
- 确保使用的是Personal Access Token，不是GitHub密码
- 检查Token是否过期
- 确认Token有 `repo` 权限

### Q: GitHub Pages显示404？

**A**: 
- 确认仓库是Public（公开）
- 检查Settings → Pages是否已启用
- 等待1-2分钟让GitHub处理

### Q: 如何查看我的GitHub用户名？

**A**: 
- 登录GitHub后，点击右上角头像
- 用户名显示在头像下方
- 或访问 https://github.com/settings/profile 查看

---

## ✅ 检查清单

部署前确认：
- [ ] Git已安装（运行 `git --version` 有输出）
- [ ] 已创建Personal Access Token并保存
- [ ] 已创建GitHub仓库（Public）
- [ ] 已复制仓库URL
- [ ] Git已配置用户名和邮箱

部署后确认：
- [ ] 文件已推送到GitHub（在仓库页面可以看到文件）
- [ ] GitHub Pages已启用（Settings → Pages）
- [ ] 网站可以访问（等待1-2分钟）

---

**按照以上步骤操作，即可成功部署！** 🎉

如有问题，请查看其他文档或联系支持。

