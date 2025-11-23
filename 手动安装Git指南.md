# 手动安装Git for Windows - 详细指南

## 📥 方法1: 官方下载（推荐）

### 步骤1: 下载Git

1. **访问官方下载页面**: https://git-scm.com/download/win
2. **自动下载**: 页面会自动检测您的系统（64位或32位）并提供下载链接
3. **点击下载**: 点击下载按钮，下载 `.exe` 安装程序

### 步骤2: 运行安装程序

1. **找到下载的文件**: 通常在 `下载` 文件夹中，文件名类似 `Git-2.43.0-64-bit.exe`
2. **双击运行**: 如果提示"是否允许此应用更改您的设备"，点击"是"

### 步骤3: 安装选项（重要）

安装过程中，建议选择以下选项：

#### 1. 选择组件（Select Components）
- ✅ **Git Bash Here** - 在右键菜单中添加Git Bash
- ✅ **Git GUI Here** - 在右键菜单中添加Git GUI
- ✅ **Associate .git* configuration files with the default text editor**
- ✅ **Associate .sh files to be run with Bash**

#### 2. 选择默认编辑器（Choosing the default editor）
- 选择您喜欢的编辑器（如Notepad++、VS Code，或使用默认的Vim）

#### 3. 调整PATH环境（Adjusting your PATH environment）
- ✅ **推荐**: 选择 "Git from the command line and also from 3rd-party software"
  - 这会将Git添加到系统PATH，可以在任何地方使用git命令

#### 4. 选择HTTPS传输后端（Choosing HTTPS transport backend）
- 使用默认选项 "Use the OpenSSL library"

#### 5. 配置行尾转换（Configuring the line ending conversions）
- ✅ **推荐**: 选择 "Checkout Windows-style, commit Unix-style line endings"

#### 6. 配置终端模拟器（Configuring the terminal emulator）
- 使用默认选项 "Use MinTTY"

#### 7. 配置额外选项（Configuring extra options）
- ✅ **启用文件系统缓存** - 提高性能
- ✅ **启用Git凭据管理器** - 方便管理GitHub凭据

#### 8. 完成安装
- 点击 "Install" 开始安装
- 等待安装完成（通常1-2分钟）
- 点击 "Finish" 完成

### 步骤4: 验证安装

1. **关闭并重新打开** PowerShell 或命令提示符
2. **运行测试命令**:
   ```bash
   git --version
   ```
3. **如果显示版本号**（如 `git version 2.43.0`），说明安装成功！

### 步骤5: 配置Git用户信息

打开新的PowerShell或命令提示符，运行：

```bash
git config --global user.email "435256553@qq.com"
git config --global user.name "syy"
```

验证配置：
```bash
git config --global --list
```

---

## 📥 方法2: 使用包管理器（高级用户）

### 使用Chocolatey

如果您已安装Chocolatey：

```bash
choco install git -y
```

### 使用Winget

Windows 10/11自带winget：

```bash
winget install --id Git.Git -e --source winget
```

---

## 🔧 如果安装后仍无法使用

### 问题1: 提示"找不到git命令"

**解决方法**:
1. **重启电脑**（最可靠的方法）
2. 或关闭并重新打开所有PowerShell/命令提示符窗口
3. 检查PATH环境变量是否包含Git路径

**手动检查PATH**:
1. 右键"此电脑" → 属性 → 高级系统设置 → 环境变量
2. 在"系统变量"中找到 `Path`
3. 检查是否包含：
   - `C:\Program Files\Git\bin`
   - `C:\Program Files\Git\cmd`
4. 如果没有，点击"编辑" → "新建" → 添加上述路径

### 问题2: 安装程序无法运行

**可能原因**:
- 需要管理员权限
- 杀毒软件阻止
- 下载的文件损坏

**解决方法**:
1. 右键安装程序 → "以管理员身份运行"
2. 临时关闭杀毒软件
3. 重新下载安装程序

### 问题3: 安装很慢

**解决方法**:
- 这是正常的，Git安装程序需要下载一些组件
- 确保网络连接正常
- 耐心等待（通常5-10分钟）

---

## ✅ 安装后检查清单

- [ ] Git已安装（运行 `git --version` 有输出）
- [ ] Git已添加到PATH（可以在任何目录使用git命令）
- [ ] 用户信息已配置（运行 `git config --global --list` 可以看到email和name）
- [ ] 可以正常使用git命令

---

## 🎯 下一步

安装完成后：

1. **配置Git用户信息**（如果还没配置）:
   ```bash
   git config --global user.email "435256553@qq.com"
   git config --global user.name "syy"
   ```

2. **创建GitHub Personal Access Token**:
   - 访问: https://github.com/settings/tokens
   - 创建新Token，权限选择 `repo`

3. **创建GitHub仓库**:
   - 访问: https://github.com/new
   - 创建Public仓库

4. **运行部署脚本**:
   - 双击 `部署到GitHub_Pages.bat`

---

## 📚 更多资源

- Git官方文档: https://git-scm.com/doc
- Git for Windows: https://git-scm.com/download/win
- GitHub指南: https://docs.github.com

---

**安装完成后，请重启PowerShell或电脑，然后运行 `git --version` 验证！** 🎉

