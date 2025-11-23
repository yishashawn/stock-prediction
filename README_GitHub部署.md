# 🚀 GitHub Pages 部署 - 快速开始

## 📋 3步完成部署

### 1️⃣ 创建GitHub仓库

访问: https://github.com/new

- **仓库名**: `stock-prediction`（或任意名称）
- **选择**: Public（公开）
- **点击**: Create repository
- **复制**: 仓库URL（例如: `https://github.com/您的用户名/stock-prediction.git`）

### 2️⃣ 创建Personal Access Token

访问: https://github.com/settings/tokens

- **点击**: Generate new token → Generate new token (classic)
- **Note**: `GitHub Pages 部署`
- **权限**: ✅ 勾选 `repo`
- **点击**: Generate token
- **复制**: Token（只显示一次，立即保存）

详细步骤: `创建GitHub_Token指南.md`

### 3️⃣ 运行部署脚本

**双击运行**: `一键部署到GitHub.bat`

按提示输入：
- GitHub仓库URL
- 提交信息（直接回车使用默认）
- 用户名: `435256553@qq.com`
- 密码: 粘贴Personal Access Token（**不是GitHub密码**）

---

## 🌐 访问网站

部署成功后，访问：

```
https://您的用户名.github.io/仓库名/
```

例如：
```
https://yishashawn.github.io/stock-prediction/
```

---

## ⚙️ 启用GitHub Pages

如果网站无法访问：

1. 访问仓库: https://github.com/您的用户名/仓库名
2. Settings → Pages
3. Source: 选择 `main` 和 `/ (root)`
4. Save
5. 等待1-5分钟生效

---

## 🔄 更新网站

每次运行预测模型后：

1. 运行: `运行预测模型.bat`（更新HTML）
2. 运行: `一键部署到GitHub.bat`（推送到GitHub）
3. 等待1-5分钟，网站自动更新

---

## 📚 详细文档

- **完整指南**: `GitHub部署完整指南.md`
- **快速指南**: `GitHub_Pages_快速指南.md`
- **Token创建**: `创建GitHub_Token指南.md`

---

## ❓ 常见问题

### 身份验证失败？

- ✅ 使用Personal Access Token（不是GitHub密码）
- ✅ 确认Token权限包含 `repo`
- ✅ 检查Token是否过期

### 网站404错误？

- ✅ 确认仓库为Public（公开）
- ✅ 检查Settings → Pages是否已启用
- ✅ 等待5-10分钟生效

### 图片无法显示？

- ✅ 确认所有PNG文件都已上传
- ✅ 检查文件名是否正确

---

**现在开始**: 运行 `一键部署到GitHub.bat` 🚀

