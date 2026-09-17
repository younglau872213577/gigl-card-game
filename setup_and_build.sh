#!/bin/bash
# ============================================================
# GI/GL 卡牌游戏 — WSL Ubuntu 一键打包脚本
# 在 WSL Ubuntu 终端中执行：bash setup_and_build.sh
# ============================================================
set -e

echo "=============================================="
echo "  GI/GL 卡牌游戏 APK 打包脚本"
echo "=============================================="

echo ""
echo "[1/5] 安装系统依赖（JDK17 / git / 编译工具）..."
sudo apt-get update
sudo apt-get install -y \
    git zip unzip openjdk-17-jdk \
    python3-pip python3-venv \
    build-essential libffi-dev libssl-dev \
    autoconf automake libtool pkg-config \
    zlib1g-dev libncurses5-dev libtinfo5

echo ""
echo "[2/5] 安装 buildozer 与 cython ..."
pip3 install --user --upgrade buildozer cython

echo ""
echo "[3/5] 复制项目到 Linux 文件系统（避免 /mnt/c 路径问题）..."
SRC="/mnt/c/Users/Administrator/Desktop/生产/GI_GL_Card_Game_Android"
DST="$HOME/gigl_card_game"
rm -rf "$DST"
mkdir -p "$DST"
cp -r "$SRC/." "$DST/"
cd "$DST"
echo "     项目已复制到：$DST"

echo ""
echo "[4/5] 配置 JAVA_HOME ..."
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
java -version

echo ""
echo "[5/5] 开始打包 APK（首次会自动下载 Android SDK/NDK，约 2~4GB，耗时 20~60 分钟）..."
echo "     之后每次打包只需几分钟。"
~/.local/bin/buildozer android debug

echo ""
echo "=============================================="
echo "  打包完成！APK 文件位于："
echo "  $DST/bin/"
echo "  文件名类似：giglcard-0.1.0-arm64-v8a-debug.apk"
echo "=============================================="
ls -la "$DST/bin/"
