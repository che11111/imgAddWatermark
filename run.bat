@echo off
chcp 65001 >nul
title 批量水印添加工具

echo =====================================
echo 批量水印添加工具 v1.0
echo =====================================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python环境
    echo 请先安装Python 3.7或更高版本
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python环境检查通过
echo.

echo 正在检查依赖包...
python -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 安装依赖包失败，请手动执行：pip install Pillow
        pause
        exit /b 1
    )
    echo 依赖包安装完成
) else (
    echo 依赖包检查通过
)

echo.
echo 正在启动水印添加工具...
echo.

python watermark_tool.py

if errorlevel 1 (
    echo.
    echo 程序运行出错，请检查错误信息
    pause
)