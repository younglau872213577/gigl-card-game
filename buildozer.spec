[app]

# 应用标题与包名
title = GI/GL 食物卡牌分类
package.name = giglcard
package.domain = org.example

# 源码目录与扩展名（otf 用于打包中文字体）
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,otf,ttc,json

# 版本
version = 0.1.0

# 运行依赖（p4a v2024.01.21 默认 Python 3.11.5，配 Kivy 2.3.1）
requirements = python3,kivy==2.3.1

# 屏幕方向（竖屏）
orientation = portrait
fullscreen = 0

# 图标与启动图
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png

# Android 配置
android.api = 33
android.minapi = 21
android.ndk = 25b
# 双架构，兼容新旧手机
android.archs = arm64-v8a, armeabi-v7a
# 自动接受 SDK 许可证（CI 非交互环境必须开启，否则 build-tools 装不上）
android.accept_sdk_license = True
# 固定 p4a v2024.01.21：python3/hostpython3 默认 3.11.5，kivy 走 CythonRecipe 源码编译，与 Kivy 2.3.1 配套
# （p4a master 已默认 Python 3.14，且 Kivy 2.3.1 无 3.14 Android wheel，故不能再用 master）
p4a.branch = v2024.01.21

[buildozer]

log_level = 2
warn_on_root = 1
