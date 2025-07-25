@echo off
echo ========================================
echo 掛機挖礦服務啟動腳本
echo ========================================
echo.

echo 正在檢查Python環境...
python --version
if errorlevel 1 (
    echo 錯誤: 未找到Python，請先安裝Python 3.7+
    pause
    exit /b 1
)

echo.
echo 正在安裝依賴...
pip install -r requirements.txt
if errorlevel 1 (
    echo 錯誤: 依賴安裝失敗
    pause
    exit /b 1
)

echo.
echo 正在啟動服務...
echo 服務地址: http://localhost:5000
echo 按 Ctrl+C 停止服務
echo.
python run.py

pause 