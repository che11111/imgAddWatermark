@echo off
chcp 65001 >nul
echo 正在打包 imgAddWatermark 程序...
echo.

REM 清理之前的构建文件
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo 开始使用 PyInstaller 打包...
pyinstaller --clean build.spec

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 打包成功！
    echo 可执行文件位置: dist\imgAddWatermark.exe
    echo ========================================
    echo.
    
    REM 复制图标文件到输出目录（如果需要）
    if exist "imgAddWatermark.ico" copy "imgAddWatermark.ico" "dist\"
    
    echo 是否要运行程序进行测试？ [Y/N]
    set /p choice=
    if /i "%choice%"=="Y" (
        echo 正在启动程序...
        start "" "dist\imgAddWatermark.exe"
    )
) else (
    echo.
    echo ========================================
    echo 打包失败！请检查错误信息。
    echo ========================================
)

echo.
pause