# GitHub Pages 部署 - 最终步骤

## ✅ 当前状态

- ✓ Git已安装并配置
- ✓ 远程仓库已配置: https://github.com/yishashawn/zhongji.git
- ✓ HTML文件已生成
- ✓ 文件已添加到Git并提交

## 🚀 最后一步：推送到GitHub

### 方法1: 使用Git命令（推荐）

打开PowerShell，运行：

```powershell
# 添加Git到PATH
$env:Path += ";C:\Program Files\Git\bin;C:\Program Files\Git\cmd"

# 进入项目目录
cd C:\Users\syy\Tushare

# 推送到GitHub
git push origin main
```

**当提示输入凭据时**:
- Username: `435256553@qq.com`（或您的GitHub用户名）
- Password: 粘贴您的Personal Access Token（不是GitHub密码）

### 方法2: 使用Git GUI

1. 右键点击项目文件夹
2. 选择 "Git GUI Here"
3. 点击 "Push"
4. 输入凭据（使用Token作为密码）

## 📝 启用GitHub Pages

推送完成后：

1. **访问仓库**: https://github.com/yishashawn/zhongji
2. **进入设置**: 点击 "Settings" 标签
3. **启用Pages**:
   - 左侧菜单找到 "Pages"
   - Source: 选择 `main` 分支
   - Folder: 选择 `/ (root)`
   - 点击 "Save"
4. **等待生效**: 通常需要1-2分钟

## 🌐 访问网站

您的网站地址：
- **主页**: https://yishashawn.github.io/zhongji/
- **预测页面**: https://yishashawn.github.io/zhongji/中际旭创_价格预测.html

## 🔄 更新网站

每次运行预测模型后，更新网站：

```powershell
# 添加Git到PATH
$env:Path += ";C:\Program Files\Git\bin;C:\Program Files\Git\cmd"

# 进入项目目录
cd C:\Users\syy\Tushare

# 添加、提交、推送
git add .
git commit -m "更新预测数据"
git push origin main
```

## ❓ 如果推送失败

### 问题: 提示"Authentication failed"

**解决**:
1. 确保已创建Personal Access Token
2. 访问: https://github.com/settings/tokens
3. 创建新Token，权限选择 `repo`
4. 使用Token作为密码（不是GitHub密码）

### 问题: 提示"Permission denied"

**解决**:
- 检查仓库URL是否正确
- 确认您有该仓库的写入权限
- 确认Token有 `repo` 权限

---

**现在运行 `git push origin main` 完成部署！** 🎯

