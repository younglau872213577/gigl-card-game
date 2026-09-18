# GI/GL 食物卡牌分类游戏（Android / Kivy）

一个面向糖友的控糖知识科普卡牌小游戏：把食物卡牌按 **GI（升糖指数）/ GL（血糖负荷）** 分类，破除「甜=高GI」「所有蔬菜都能随便吃」等锚定误区。

## 技术栈

- **UI**：Kivy 2.3.1（Android 版重写；数据/逻辑层复用桌面版）
- **数据层**：`card_data.py`（卡牌库 + 关卡定义）
- **逻辑层**：`game_logic.py`（抽卡、判分，无 GUI 依赖）
- **打包**：buildozer 1.5.0 + python-for-android，GitHub Actions 云端打包

## 项目结构

```
main.py               # Kivy 主程序（UI + 交互）
card_data.py          # 卡牌数据库 + 关卡定义（数据层，勿改内容）
game_logic.py         # 纯逻辑层（抽卡/判分，可独立测试）
buildozer.spec        # 打包配置（★关键坑都在这里）
.github/workflows/build.yml  # GitHub Actions 自动打包
NotoSansSC-Regular.otf  # 中文字体（打包进 APK）
NotoEmoji.ttf          # emoji 字体（卡片食物图标背景）
icon.png / presplash.png
```

## 本地运行（Windows）

```bash
python main.py
```

> 需本机装有 Kivy：`pip install kivy==2.3.1`。中文字体会自动回退到 `C:/Windows/Fonts/msyh.ttc`（微软雅黑）。

## 打包 APK（GitHub Actions，推荐）

改完代码 → 提交推送 → 云端自动出 APK：

```bash
git add .
git commit -m "描述改动"
git push origin main
```

推送后打开仓库 → **Actions** 标签，等「Build Android APK」变绿勾 → 页面底部 **Artifacts** 下载 `giglcard-apk` zip → 解压出 `.apk` 安装。

首次打包约 30~60 分钟（下载 SDK/NDK），之后约 15~30 分钟。

---

## ⚠️ 关键坑（务必遵守，踩过血的教训）

### 1. p4a.branch 必须固定，绝不能用 master

`buildozer.spec` 里：

```
p4a.branch = v2024.01.21
```

原因：p4a 的 `master` 分支（2026 起）默认 Python **3.14**，而 Kivy 2.3.1 **没有** 3.14 的 Android wheel，会编译失败。必须固定到 `v2024.01.21`（Python 3.11.5），源码编译才能成功。

### 2. requirements 必加 filetype

```
requirements = python3,kivy==2.3.1,filetype
```

Kivy 2.3.1 的 `kivy/core/image/__init__.py` 硬依赖 `filetype`。漏加 → APK 能装但**启动即闪退**，logcat 报 `ModuleNotFoundError: No module named 'filetype'`。

### 3. FloatLayout 里精确定位的控件必须设 size_hint=(None,None)

Button / Widget / Label 默认 `size_hint=(1,1)`，会被 FloatLayout 强制撑满全屏，覆盖手动设的 `size`。

**凡是用了 `pos=...` + `size=...` 定位的控件，都要补 `size_hint=(None, None)`**，否则布局全乱、控件叠满屏。

### 4. emoji 必须打包字体

Kivy 默认 Roboto **不含 emoji**，Android 上不会自动回退系统字体，emoji 会显示成方框。

做法：`NotoEmoji.ttf`（约 2MB）放源码根目录，代码里注册并使用：

```python
from kivy.core.text import LabelBase
LabelBase.register(name="EMOJI", fn_regular="NotoEmoji.ttf")
# emoji 的 Label 指定 font_name="EMOJI"
```

`source.include_exts` 已含 `ttf`，会自动打进 APK。

### 5. 圆角/阴影用 canvas 指令，颜色切换改 Color 指令

鸿蒙风圆角卡片：

```python
from kivy.graphics import Color, RoundedRectangle, Line
with widget.canvas.before:
    Color(*shadow)                    # 阴影层
    RoundedRectangle(pos=..., size=..., radius=[dp(12)])
    self.bg_color = Color(*bg)        # 保存 Color 引用，用于切色
    self.bg_rect = RoundedRectangle(pos=..., size=..., radius=[dp(12)])
    self.border_color = Color(*border)
    self.border_line = Line(rounded_rectangle=(x, y, w, h, r), width=1.2)
```

改颜色必须 `self.bg_color.rgba = ...`，**不能**设 `RoundedRectangle.rgba`（无此属性）。

### 6. 推送走 SSH 通道

Git 2.55 的 HTTPS/libcurl 有 libidn2 DLL bug（`STATUS_ENTRYPOINT_NOT_FOUND`），push 会挂。改用 SSH：

```bash
git remote set-url origin git@github.com:younglau872213577/gigl-card-game.git
git config core.sshCommand "ssh -i <deploy_key路径> -o StrictHostKeyChecking=accept-new"
```

## 数据边界归类（按脚本文本）

- 哈密瓜 70 / 荔枝 70 → 归 **高GI**（关卡1）
- 胡萝卜 71 → 归 **中GI**（关卡2，脚本原文如此，与严格 GI 数值推导略有出入）

如需严格按 GI 数值推导，可再调整。

## 仓库信息

- 仓库：`git@github.com:younglau872213577/gigl-card-game.git`（Public）
- 账号：`younglau872213577`（邮箱 liueason@163.com）
- 本地路径：`C:\Users\Administrator\Desktop\生产\GI_GL_Card_Game_Android\`
