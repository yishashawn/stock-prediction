# 创建GitHub Personal Access Token 指南

## ⚠️ 重要提示

GitHub 从 2021年8月13日起，不再支持使用密码进行 Git 操作。必须使用 **Personal Access Token (PAT)**。

## 📝 创建Token步骤

### 步骤1: 登录GitHub

1. 访问: https://github.com/login
2. 使用您的账号登录: **435256553@qq.com**

### 步骤2: 创建Personal Access Token

1. **访问Token设置页面**:
   - 直接访问: https://github.com/settings/tokens
   - 或: 点击右上角头像 → Settings → 左侧菜单最下方 "Developer settings" → "Personal access tokens" → "Tokens (classic)"

2. **生成新Token**:
   - 点击 "Generate new token" → 选择 "Generate new token (classic)"
   - 如果提示输入密码，请输入您的GitHub密码: **jjjydxm6**

3. **设置Token信息**:
   - **Note（备注）**: `GitHub Pages 部署`（或任意名称）
   - **Expiration（过期时间）**: 选择 "90 days" 或 "No expiration"（无过期）
   - **Select scopes（选择权限）**: 
     - ✅ 勾选 `repo`（完整仓库权限）
     - ✅ 勾选 `workflow`（如果需要GitHub Actions）

4. **生成Token**:
   - 滚动到页面底部
   - 点击 "Generate token"（绿色按钮）

5. **复制Token**:
   - ⚠️ **重要**: Token只显示一次，请立即复制并保存
   - Token格式类似: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 步骤3: 保存Token

将Token保存在安全的地方，例如：
- 密码管理器（推荐）
- 本地文本文件（加密）
- 环境变量

## 🔐 使用Token

### 方法1: 在Git命令中使用

当Git提示输入密码时：
- **用户名**: `435256553@qq.com`（或您的GitHub用户名）
- **密码**: 粘贴刚才复制的Token（不是GitHub密码）

### 方法2: 配置Git凭据（Windows）

```bash
# 使用Git凭据管理器存储Token
git config --global credential.helper manager-core
```

然后在使用时输入Token，Git会记住它。

### 方法3: 在URL中使用（不推荐，安全性较低）

```bash
git remote set-url origin https://ghp_您的Token@github.com/用户名/仓库名.git
```

## ✅ 验证Token

测试Token是否有效：

```bash
# 测试访问（会提示输入用户名和密码，密码处输入Token）
git ls-remote https://github.com/您的用户名/测试仓库.git
```

## 🔄 更新网站时使用

每次运行 `部署到GitHub_Pages.bat` 时：
1. 当提示输入用户名：输入 `435256553@qq.com`
2. 当提示输入密码：粘贴您的Personal Access Token

## ⚠️ 安全建议

1. **不要分享Token**: Token等同于密码，不要分享给他人
2. **定期更新**: 建议每90天更新一次Token
3. **限制权限**: 只授予必要的权限（repo即可）
4. **撤销旧Token**: 如果Token泄露，立即在GitHub设置中撤销

## 🆘 如果Token泄露

1. 立即访问: https://github.com/settings/tokens
2. 找到泄露的Token
3. 点击 "Revoke"（撤销）
4. 创建新Token

---

**创建Token后，请运行 `部署到GitHub_Pages.bat` 开始部署！**

