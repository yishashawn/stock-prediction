# Netlify部署指南 - 最简单公网访问方案

## 🎯 为什么选择Netlify？

- ✅ **最简单**：拖拽文件即可，无需Git、无需命令行
- ✅ **完全免费**：无限流量和带宽
- ✅ **全球CDN**：访问速度快
- ✅ **自动HTTPS**：安全连接
- ✅ **即时生效**：上传后几秒钟即可访问

## 📋 详细步骤

### 步骤1: 准备文件

1. **运行**: `使用Netlify部署.bat`
2. 脚本会自动：
   - 检查HTML文件是否存在
   - 创建部署文件夹 `netlify_deploy`
   - 复制所有需要的文件
   - 打开文件夹

### 步骤2: 访问Netlify

1. **打开浏览器**，访问: https://www.netlify.com/
2. **注册/登录**:
   - 点击右上角 "Sign up"
   - 可以用GitHub账号登录（推荐，一键登录）
   - 或用邮箱注册（需要验证邮箱）

### 步骤3: 部署网站

1. **登录后**，在Netlify首页会看到一个大框：
   ```
   Want to deploy a new site without connecting to Git?
   Drag and drop your site output folder here
   ```

2. **拖拽文件夹**:
   - 打开 `netlify_deploy` 文件夹（脚本已自动打开）
   - **将整个文件夹拖拽**到Netlify页面的拖拽区域
   - 或点击 "Browse to upload" 选择文件夹

3. **等待部署**:
   - Netlify会自动上传文件
   - 通常需要10-30秒
   - 部署完成后会显示成功消息

### 步骤4: 获得网站地址

部署完成后，Netlify会显示：

- **网站地址**: 例如 `https://random-name-12345.netlify.app`
- **状态**: "Published"（已发布）

**这个地址可以在任何地方访问！** 🌐

### 步骤5: 访问网站

在浏览器中打开Netlify提供的地址，例如：
```
https://random-name-12345.netlify.app/中际旭创_价格预测.html
```

或如果上传了 `index.html`，可以直接访问：
```
https://random-name-12345.netlify.app/
```

## 🔄 更新网站

每次运行预测模型后，更新网站：

### 方法1: 重新拖拽（简单）

1. 运行 `使用Netlify部署.bat`（会重新生成文件夹）
2. 在Netlify网站中，找到您的网站
3. 点击网站卡片
4. 在 "Deploys" 标签页，拖拽新的文件夹
5. 等待更新完成

### 方法2: 使用Netlify CLI（高级）

1. 安装Netlify CLI: `npm install -g netlify-cli`
2. 运行: `netlify deploy --prod --dir=netlify_deploy`

## 🎨 自定义域名（可选）

1. **在Netlify网站中**，点击您的网站
2. **进入**: Site settings → Domain management
3. **添加域名**: 输入您的域名
4. **配置DNS**: 按照Netlify的提示配置DNS记录

## 📱 分享网站

获得Netlify地址后，您可以：

- **分享给任何人**：发送Netlify地址即可
- **在任何设备访问**：手机、平板、电脑都可以
- **无需同一网络**：只要有网络就能访问

## ❓ 常见问题

### Q: 拖拽后显示错误？

**A**: 
- 确保拖拽的是文件夹，不是单个文件
- 确保HTML文件在文件夹根目录
- 检查文件大小（Netlify免费版限制100MB）

### Q: 图片无法显示？

**A**: 
- 确保PNG文件与HTML在同一文件夹
- 检查HTML中的图片路径是否正确

### Q: 如何删除网站？

**A**: 
- 在Netlify网站中，进入Site settings
- 滚动到底部，点击 "Delete site"

### Q: 可以绑定自己的域名吗？

**A**: 
- 可以，在Domain management中添加自定义域名
- 需要配置DNS记录指向Netlify

## 🆚 与其他方案对比

| 特性 | Netlify | GitHub Pages | 本地服务器 |
|------|---------|--------------|------------|
| 公网访问 | ✅ | ✅ | ❌ |
| 部署难度 | ⭐ 最简单 | ⭐⭐ 中等 | ⭐⭐⭐ 复杂 |
| 更新方式 | 拖拽 | Git推送 | 手动 |
| 访问速度 | 快 | 中等 | 本地快 |
| 需要账号 | 是 | 是 | 否 |

---

**现在运行 `使用Netlify部署.bat` 开始部署！** 🚀

