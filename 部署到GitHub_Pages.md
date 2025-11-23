# 将中际旭创价格预测网站部署到GitHub Pages

GitHub Pages 是一个免费的静态网站托管服务，可以让您的网站通过公网访问。

## 步骤1: 创建GitHub仓库

1. 登录 [GitHub](https://github.com)
2. 点击右上角的 "+" 号，选择 "New repository"
3. 仓库名称：`stock-prediction`（或您喜欢的名称）
4. 选择 "Public"（公开，才能使用免费版GitHub Pages）
5. 勾选 "Add a README file"
6. 点击 "Create repository"

## 步骤2: 上传文件到GitHub

### 方法1: 使用Git命令行（推荐）

```bash
# 1. 初始化Git仓库
git init

# 2. 添加远程仓库（替换 YOUR_USERNAME 为您的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/stock-prediction.git

# 3. 添加文件
git add 中际旭创_价格预测.html
git add 中际旭创_价格预测模型.png
git add 中际旭创_多因素散点图.png
git add 中际旭创_特征重要性详细分析.png
git add 中际旭创_所有因素散点图_第1页.png
git add README.md

# 4. 提交
git commit -m "Initial commit: 中际旭创股票价格预测网站"

# 5. 推送到GitHub
git branch -M main
git push -u origin main
```

### 方法2: 使用GitHub网页界面

1. 在GitHub仓库页面，点击 "uploading an existing file"
2. 将以下文件拖拽上传：
   - `中际旭创_价格预测.html`
   - `中际旭创_价格预测模型.png`
   - `中际旭创_多因素散点图.png`
   - `中际旭创_特征重要性详细分析.png`
   - `中际旭创_所有因素散点图_第1页.png`
3. 点击 "Commit changes"

## 步骤3: 启用GitHub Pages

1. 在GitHub仓库页面，点击 "Settings"（设置）
2. 在左侧菜单中找到 "Pages"
3. 在 "Source" 部分，选择 "main" 分支和 "/ (root)" 文件夹
4. 点击 "Save"
5. 等待几分钟，GitHub会生成您的网站地址：
   `https://YOUR_USERNAME.github.io/stock-prediction/中际旭创_价格预测.html`

## 步骤4: 设置默认首页（可选）

为了让访问更简单，可以创建一个 `index.html` 文件，自动跳转到预测页面：

1. 在仓库根目录创建 `index.html`，内容如下：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url=中际旭创_价格预测.html">
    <title>中际旭创股票价格预测</title>
</head>
<body>
    <p>正在跳转到预测页面...</p>
    <p>如果未自动跳转，请<a href="中际旭创_价格预测.html">点击这里</a></p>
</body>
</html>
```

2. 上传 `index.html` 到仓库
3. 现在可以直接访问：`https://YOUR_USERNAME.github.io/stock-prediction/`

## 步骤5: 自动更新（可选）

每次运行预测模型后，可以自动更新GitHub Pages：

1. 创建一个更新脚本 `update_github_pages.py`：

```python
import subprocess
import os

# 切换到项目目录
os.chdir(r'C:\Users\syy\Tushare')

# Git命令
commands = [
    'git add 中际旭创_价格预测.html',
    'git add 中际旭创_价格预测模型.png',
    'git add 中际旭创_多因素散点图.png',
    'git add 中际旭创_特征重要性详细分析.png',
    'git add 中际旭创_所有因素散点图_第1页.png',
    'git commit -m "更新预测数据"',
    'git push'
]

for cmd in commands:
    print(f'执行: {cmd}')
    subprocess.run(cmd, shell=True)

print('GitHub Pages 已更新！')
```

2. 在 `predict_stock_price_advanced.py` 的最后添加：

```python
# 可选：自动更新GitHub Pages
# import subprocess
# subprocess.run(['python', 'update_github_pages.py'])
```

## 注意事项

1. **文件大小限制**：GitHub Pages 单个文件限制为 100MB
2. **访问速度**：GitHub Pages 在国内访问可能较慢，可以使用CDN加速
3. **更新频率**：GitHub Pages 更新后需要几分钟才能生效
4. **隐私**：公开仓库意味着所有人都能看到您的代码和数据

## 其他免费托管选项

- **Netlify**: https://www.netlify.com/ （支持拖拽部署）
- **Vercel**: https://vercel.com/ （支持GitHub自动部署）
- **Cloudflare Pages**: https://pages.cloudflare.com/ （速度快）

