@echo off
chcp 65001 >nul
echo =====================================
echo   演出经纪人继续教育刷课助手 — 安装
echo =====================================
echo.

:: 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 请先安装 Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [✓] Python 已安装

:: 创建虚拟环境
if not exist venv (
    echo [*] 创建虚拟环境...
    python -m venv venv
)
echo [✓] 虚拟环境就绪

:: 激活虚拟环境
call venv\Scripts\activate.bat

:: 安装依赖
echo [*] 安装 browser-use (可能需要几分钟)...
pip install browser-use playwright python-dotenv -q
echo [✓] browser-use 安装完成

:: 安装 Chromium 浏览器
echo [*] 安装 Chromium 浏览器 (首次约 150MB)...
playwright install chromium
echo [✓] Chromium 安装完成

:: 检查 .env 文件
if not exist .env (
    echo [*] 创建 .env 配置文件...
    echo DEEPSEEK_API_KEY=请替换为你的API_KEY > .env
    echo DEEPSEEK_BASE_URL=https://api.deepseek.com/v1 >> .env
    echo.
    echo ⚠️  请编辑 .env 文件，填入你的 DeepSeek API Key
    echo    获取地址: https://platform.deepseek.com/api_keys
    echo    新用户免费赠送 500万 token
)

echo.
echo =====================================
echo   安装完成！
echo.
echo   下一步:
echo   1. 编辑 .env 填入 DeepSeek API Key
echo   2. 运行: main.bat
echo =====================================
pause
