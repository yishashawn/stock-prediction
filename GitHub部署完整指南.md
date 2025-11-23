# 🚀 GitHub Pages 完整部署指南

## 📋 前置要求

1. ✅ **GitHub账号**: 如果没有，访问 https://github.com/signup 注册
2. ✅ **Git已安装**: 运行 `安装Git_简化版.bat` 或访问 https://git-scm.com/download/win
3. ✅ **已生成HTML文件**: 运行 `运行预测模型.bat` 生成预测页面

---

## 🎯 快速开始（3步）

### 步骤1: 创建GitHub仓库

1. **访问**: https://github.com/new
2. **填写信息**:
   - **Repository name**: `stock-prediction`（或任意名称）
   - **Description**: `中际旭创股票价格预测`（可选）
   - **Visibility**: 选择 **Public**（公开，才能使用免费GitHub Pages）
3. **点击**: "Create repository"（绿色按钮）
4. **复制仓库URL**: 
   - 例如: `https://github.com/您的用户名/stock-prediction.git`
   - ⚠️ 保存这个URL，后面会用到

### 步骤2: 创建Personal Access Token

⚠️ **重要**: GitHub已不支持使用密码，必须使用Token！

1. **访问**: https://github.com/settings/tokens
2. **点击**: "Generate new token" → "Generate new token (classic)"
3. **设置**:
   - **Note**: `GitHub Pages 部署`
   - **Expiration**: 选择 `90 days` 或 `No expiration`
   - **Select scopes**: ✅ 勾选 `repo`（完整仓库权限）
4. **点击**: "Generate token"（绿色按钮）
5. **复制Token**: 
   - ⚠️ **只显示一次**，立即复制保存
   - 格式: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

详细步骤请查看: `创建GitHub_Token指南.md`

### 步骤3: 运行部署脚本

1. **双击运行**: `一键部署到GitHub.bat`
2. **按提示操作**:
   - 输入GitHub仓库URL（步骤1中复制的）
   - 输入提交信息（直接回车使用默认）
   - 确认推送
3. **输入凭据**（当提示时）:
   - **用户名**: `435256553@qq.com`（或您的GitHub用户名）
   - **密码**: 粘贴Personal Access Token（**不是GitHub密码**）

---

## 🌐 访问您的网站

部署成功后，您的网站地址为：

```
https://您的用户名.github.io/仓库名/
```

例如：
```
https://yishashawn.github.io/stock-prediction/
```

### 完整页面地址

- **主页（自动跳转）**: `https://您的用户名.github.io/仓库名/`
- **预测页面**: `https://您的用户名.github.io/仓库名/中际旭创_价格预测.html`

---

## ⚙️ 启用GitHub Pages

如果网站无法访问，请检查：

1. **访问仓库**: https://github.com/您的用户名/仓库名
2. **进入设置**: Settings → Pages
3. **配置Source**:
   - **Source**: 选择 `Deploy from a branch`
   - **Branch**: 选择 `main` 和 `/ (root)`
4. **点击**: "Save"
5. **等待**: 通常需要1-5分钟生效

---

## 🔄 更新网站

每次运行预测模型后，更新网站：

1. **运行**: `运行预测模型.bat`（更新HTML文件）
2. **运行**: `一键部署到GitHub.bat`（推送到GitHub）
3. **等待**: 1-5分钟后网站自动更新

---

## 📁 部署的文件

以下文件会被上传到GitHub：

- ✅ `中际旭创_价格预测.html` - 主页面
- ✅ `中际旭创_价格预测模型.png` - 模型图表
- ✅ `中际旭创_多因素散点图.png` - 散点图
- ✅ `中际旭创_特征重要性详细分析.png` - 特征分析
- ✅ `中际旭创_所有因素散点图_第1页.png` - 所有因素图
- ✅ `index.html` - 自动跳转页面（自动创建）

---

## ❓ 常见问题

### Q1: 提示 "Authentication failed"（身份验证失败）

**原因**: 使用了GitHub密码而不是Token

**解决**:
1. 确保已创建Personal Access Token
2. 当提示输入密码时，粘贴Token（不是密码）
3. 如果还是失败，检查Token是否过期或被撤销

### Q2: 提示 "Repository not found"（仓库未找到）

**原因**: 仓库不存在或URL错误

**解决**:
1. 确认仓库已创建且为Public
2. 检查仓库URL是否正确
3. 确认您有该仓库的访问权限

### Q3: 网站显示 404 Not Found

**原因**: GitHub Pages未启用或配置错误

**解决**:
1. 检查仓库设置 → Pages → Source 是否设置为 `main` 分支
2. 确认仓库为Public（公开）
3. 等待5-10分钟，GitHub Pages需要时间生效

### Q4: 图片无法显示

**原因**: 图片路径或文件名问题

**解决**:
1. 确认所有PNG文件都已上传
2. 检查HTML中的图片路径是否正确
3. 确保文件名与HTML中的引用一致

### Q5: 中文文件名显示乱码

**原因**: Git编码问题

**解决**:
- 脚本已自动处理中文文件名
- 如果仍有问题，检查Git配置：
  ```bash
  git config --global core.quotepath false
  git config --global i18n.commitencoding utf-8
  ```

### Q6: 推送时提示 "fatal: could not read Username"

**原因**: Git凭据未配置

**解决**:
1. 使用Personal Access Token作为密码
2. 配置Git凭据管理器：
   ```bash
   git config --global credential.helper manager-core
   ```

---

## 🔐 安全建议

1. **不要分享Token**: Token等同于密码
2. **定期更新Token**: 建议每90天更新一次
3. **限制权限**: 只授予必要的权限（repo即可）
4. **撤销泄露Token**: 如果Token泄露，立即在GitHub设置中撤销

---

## 📝 详细文档

- **创建Token**: `创建GitHub_Token指南.md`
- **快速指南**: `GitHub_Pages_快速指南.md`
- **完整说明**: `部署到GitHub_Pages.md`

---

## 🎉 完成！

部署成功后，您的网站就可以被任何人访问了！

**分享给他人**: 发送GitHub Pages地址即可，无需在同一网络。

---

**现在开始**: 运行 `一键部署到GitHub.bat` 🚀

