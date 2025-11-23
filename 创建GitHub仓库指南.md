# 📦 创建GitHub仓库指南

## 🎯 快速步骤

### 步骤1: 登录GitHub

1. 访问: https://github.com/login
2. 使用您的账号登录: `435256553@qq.com`

### 步骤2: 创建新仓库

1. **访问创建页面**: https://github.com/new
   - 或点击右上角 "+" → "New repository"

2. **填写仓库信息**:
   - **Repository name（仓库名称）**: `stock-prediction`（或任意名称，例如: `zhongji`）
   - **Description（描述）**: `中际旭创股票价格预测`（可选）
   - **Visibility（可见性）**: 
     - ✅ **Public**（公开）- **必须选择这个！** GitHub Pages免费版只支持公开仓库
     - ❌ Private（私有）- 不支持免费GitHub Pages

3. **其他选项**:
   - ❌ **不要**勾选 "Add a README file"（脚本会自动处理）
   - ❌ **不要**勾选 "Add .gitignore"（脚本会自动创建）
   - ❌ **不要**勾选 "Choose a license"

4. **点击**: "Create repository"（绿色按钮）

### 步骤3: 复制仓库URL

创建成功后，GitHub会显示仓库页面，您会看到：

```
Quick setup — if you've done this kind of thing before
https://github.com/您的用户名/stock-prediction.git
```

**复制这个URL**，格式类似：
```
https://github.com/yishashawn/stock-prediction.git
```

⚠️ **注意**: 
- 确保URL以 `.git` 结尾
- 确保仓库是 **Public**（公开）

---

## ✅ 验证仓库

### 检查仓库是否存在

1. 访问: `https://github.com/您的用户名/仓库名`
2. 如果能看到仓库页面，说明创建成功
3. 如果显示 404，说明仓库不存在或名称错误

### 检查仓库是否为Public

1. 在仓库页面，查看右上角
2. 如果显示 "Public" 标签，说明是公开仓库 ✅
3. 如果显示 "Private"，需要改为Public：
   - Settings → Danger Zone → Change visibility → Change to public

---

## 🔧 如果仓库已存在但推送失败

### 问题1: 仓库名称错误

**症状**: `remote: Repository not found`

**解决**:
1. 检查仓库URL是否正确
2. 确认用户名和仓库名拼写正确
3. 访问仓库页面验证: `https://github.com/您的用户名/仓库名`

### 问题2: 仓库是Private

**症状**: 推送成功但GitHub Pages无法访问

**解决**:
1. 进入仓库: Settings → Danger Zone
2. Change visibility → Change to public
3. 确认更改

### 问题3: 没有仓库访问权限

**症状**: `remote: Repository not found` 或 `Permission denied`

**解决**:
1. 确认您登录的是正确的GitHub账号
2. 确认仓库是您自己创建的（不是别人的仓库）
3. 检查Personal Access Token权限是否包含 `repo`

---

## 📝 推荐的仓库名称

- `stock-prediction` - 股票预测
- `zhongji-stock` - 中际旭创股票
- `stock-forecast` - 股票预测
- `zhongji` - 中际旭创（简短）

**注意**: 仓库名称只能包含：
- 字母（a-z, A-Z）
- 数字（0-9）
- 连字符（-）
- 下划线（_）
- 点（.）

不能包含空格或特殊字符。

---

## 🚀 创建完成后

1. **复制仓库URL**
2. **运行**: `一键部署到GitHub.bat`
3. **输入**: 刚才复制的仓库URL
4. **继续**: 按提示完成部署

---

## ❓ 常见问题

### Q: 可以修改仓库名称吗？

**A**: 可以
1. 进入仓库: Settings → General
2. 滚动到 "Repository name"
3. 修改名称并保存
4. 更新本地Git的远程URL：
   ```bash
   git remote set-url origin https://github.com/您的用户名/新名称.git
   ```

### Q: 仓库创建后可以删除吗？

**A**: 可以
1. 进入仓库: Settings → Danger Zone
2. Delete this repository
3. 输入仓库名称确认删除

### Q: 一个账号可以创建多少个仓库？

**A**: 
- 免费账号: 无限个公开仓库
- 私有仓库: 免费账号有数量限制

---

**现在去创建仓库**: https://github.com/new 🚀

