# GI/GL 卡牌游戏 — GitHub 云端打包指南（免 WSL、免重启）

> 已配置好 GitHub Actions 自动打包：把代码推到 GitHub，云端自动编译出 APK。
> 你只需要做一次「建仓库 + 推代码」，之后每次改代码推上去都会自动出 APK。

---

## 第 1 步：在 GitHub 网页创建仓库

1. 打开 https://github.com ，用你的账号（liueason@163.com）登录
2. 点右上角 **`+`** → **New repository**
3. Repository name 填：**`gigl-card-game`**
4. 选择 **Public**（公开，免费额度充足）
5. **不要**勾选 "Add a README"（保持空仓库）
6. 点 **Create repository**

> 创建后网页会停在一个「Quick setup」页面，先别关，后面要用。

## 第 2 步：安装 Git（本机，只需一次）

用浏览器打开，下载并双击安装（一路下一步即可）：

```
https://git-scm.com/download/win
```

装完后，**关掉所有命令行窗口**，重新打开一个新的。

## 第 3 步：推送代码到 GitHub

打开 **PowerShell**（普通权限即可），把下面整段复制进去、回车执行（会自动进入项目目录、初始化并推送）：

```powershell
cd "C:\Users\Administrator\Desktop\生产\GI_GL_Card_Game_Android"

git init
git add .
git commit -m "GI/GL 卡牌游戏 Android 版"
git branch -M main
git remote add origin https://github.com/你的用户名/gigl-card-game.git
git push -u origin main
```

> ⚠️ 把上面最后一行里的「**你的用户名**」换成你的 GitHub 用户名（注册时用的英文名，不是邮箱）。
>
> 执行 `git push` 时如果弹出登录窗口，用 GitHub 账号登录即可（现在 GitHub 用 Personal Access Token 或浏览器授权）。

## 第 4 步：等云端自动打包

推上去后，GitHub 会自动开始打包：
1. 打开你的仓库网页 → 点 **Actions** 标签
2. 会看到「Build Android APK」正在跑（黄色圆点在转）
3. 等它变**绿色对勾**（首次约 30~60 分钟，因为要下载 Android SDK/NDK）

## 第 5 步：下载 APK

1. 在 Actions 页点进那次**绿色对勾**的运行记录
2. 页面底部 **Artifacts** 区域，点 **`giglcard-apk`** 下载
3. 解压 zip，里面的 `.apk` 文件发到手机安装即可

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 忘记 GitHub 用户名 | 登录 github.com 后点右上角头像，下拉里显示的就是 |
| git push 报 403 / 认证失败 | 需要 Personal Access Token 或浏览器登录弹窗，见下方补充 |
| Actions 里红色叉叉 | 点进去看报错日志，发给我帮你改 |
| 想改代码重新出 APK | 本地改完，再跑 `git add .` + `git commit` + `git push` 即可 |

---

## 补充：git push 认证（新版 GitHub）

2024 年后 GitHub 不再支持密码登录 git，需要用 **Personal Access Token** 当作密码：

1. GitHub 网页 → 右上角头像 → **Settings** → 左下 **Developer settings**
2. → **Personal access tokens** → **Tokens (classic)** → **Generate new token (classic)**
3. 勾选 **`repo`** 权限，有效期随便，点 Generate
4. 复制生成的那串 `ghp_...` 令牌
5. `git push` 时，用户名填你的 GitHub 用户名，**密码填这串令牌**

> 或者更简单：执行 `git push` 时如果弹出浏览器授权，直接点授权即可。
