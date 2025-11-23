# GitHub Pages 快速部署指南

## 🚀 方法1: 使用自动部署脚本（推荐）

### 步骤1: 准备GitHub仓库

1. **登录GitHub**: https://github.com
2. **创建新仓库**:
   - 点击右上角 "+" → "New repository"
   - 仓库名称: `stock-prediction`（或任意名称）
   - 选择 **Public**（公开，才能使用免费GitHub Pages）
   - **不要**勾选 "Add a README file"（脚本会自动处理）
   - 点击 "Create repository"
3. **复制仓库URL**: 例如 `https://github.com/您的用户名/stock-prediction.git`

### 步骤2: 运行自动部署脚本

1. **双击运行** `部署到GitHub_Pages.bat`
2. 按照提示操作：
   - 如果是第一次，脚本会自动初始化Git仓库
   - 输入GitHub仓库URL
   - 输入提交信息（或直接回车使用默认）
   - 确认推送

### 步骤3: 启用GitHub Pages

1. 在GitHub仓库页面，点击 **Settings**（设置）
2. 左侧菜单找到 **Pages**
3. 在 **Source** 部分：
   - Branch: 选择 `main`
   - Folder: 选择 `/ (root)`
4. 点击 **Save**
5. 等待1-2分钟，GitHub会生成网站地址

### 步骤4: 访问网站

您的网站地址：
- **主页**: `https://您的用户名.github.io/仓库名/`
- **预测页面**: `https://您的用户名.github.io/仓库名/中际旭创_价格预测.html`

---

## 📝 方法2: 手动部署（适合熟悉Git的用户）

### 步骤1: 初始化Git仓库

```bash
# 在项目目录中运行
git init
git add 中际旭创_价格预测.html
git add 中际旭创_价格预测模型.png
git add 中际旭创_多因素散点图.png
git add 中际旭创_特征重要性详细分析.png
git add 中际旭创_所有因素散点图_第1页.png
git commit -m "Initial commit: 中际旭创股票价格预测"
```

### 步骤2: 连接到GitHub

```bash
# 替换为您的仓库URL
git remote add origin https://github.com/您的用户名/仓库名.git
git branch -M main
git push -u origin main
```

### 步骤3: 启用GitHub Pages

同方法1的步骤3

---

## 🔐 身份验证问题

如果推送时提示身份验证失败：

### 方法A: 使用Personal Access Token（推荐）

1. **生成Token**:
   - 访问: https://github.com/settings/tokens
   - 点击 "Generate new token" → "Generate new token (classic)"
   - 名称: `GitHub Pages Deploy`
   - 权限: 勾选 `repo`（完整仓库权限）
   - 点击 "Generate token"
   - **复制Token**（只显示一次，请保存）

2. **使用Token**:
   - 用户名: 您的GitHub用户名
   - 密码: 粘贴刚才复制的Token（不是GitHub密码）

### 方法B: 使用SSH密钥

1. **生成SSH密钥**:
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. **添加到GitHub**:
   - 复制 `~/.ssh/id_ed25519.pub` 的内容
   - 访问: https://github.com/settings/keys
   - 点击 "New SSH key"
   - 粘贴公钥内容
   - 点击 "Add SSH key"

3. **使用SSH URL**:
   ```bash
   git remote set-url origin git@github.com:用户名/仓库名.git
   ```

---

## 🔄 更新网站

每次运行预测模型后，更新网站：

### 使用自动脚本

1. 运行 `predict_stock_price_advanced.py` 生成新的HTML
2. 运行 `部署到GitHub_Pages.bat`
3. 输入提交信息，确认推送

### 手动更新

```bash
git add 中际旭创_价格预测.html
git add *.png
git commit -m "更新预测数据"
git push
```

---

## ❓ 常见问题

### Q: GitHub Pages 显示 404 错误？

**A**: 可能的原因：
1. **仓库不是Public**: GitHub Pages免费版只支持公开仓库
2. **Pages未启用**: 检查 Settings → Pages 是否已设置
3. **文件路径错误**: 确保文件名正确（区分大小写）
4. **等待时间**: GitHub Pages需要1-2分钟才能生效

### Q: 图片无法显示？

**A**: 
- 确保所有PNG文件都已上传到GitHub
- 检查HTML中的图片路径是否正确
- 清除浏览器缓存后重试

### Q: 如何自定义域名？

**A**:
1. 在仓库 Settings → Pages → Custom domain 输入您的域名
2. 在域名DNS中添加CNAME记录指向 `您的用户名.github.io`

### Q: 访问速度慢？

**A**: 
- GitHub Pages在国内访问可能较慢
- 可以使用VPN/代理加速
- 或考虑使用国内CDN服务

---

## 📚 更多资源

- GitHub Pages文档: https://docs.github.com/pages
- Git官方文档: https://git-scm.com/doc
- 问题反馈: 在GitHub仓库中创建Issue

---

## ✅ 检查清单

部署前请确认：
- [ ] GitHub仓库已创建（Public）
- [ ] 所有文件已生成（HTML和PNG）
- [ ] Git已安装
- [ ] 已准备好Personal Access Token或SSH密钥
- [ ] GitHub Pages已启用（Settings → Pages）

部署后请确认：
- [ ] 网站可以访问
- [ ] 所有图片正常显示
- [ ] 图表正常加载
- [ ] 移动端显示正常

---

**祝您部署顺利！** 🎉

