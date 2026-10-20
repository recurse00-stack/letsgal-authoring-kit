@echo off
chcp 65001 >nul
cd /d "%~dp0"
python -B install.py
if errorlevel 1 goto end
echo.
choice /C YN /N /M "按 Y 安装以上内容，按 N 退出："
if errorlevel 2 goto end
python -B install.py --apply
:end
pause
