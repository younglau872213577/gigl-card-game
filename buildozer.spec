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

# 运行依赖
requirements = python3,kivy

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

[buildozer]

log_level = 2
warn_on_root = 1
