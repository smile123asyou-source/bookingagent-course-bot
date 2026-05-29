"""
一键生成「演出经纪人刷课助手」全部文件
把这段代码保存为 setup.py，放到你想放项目的目录，然后运行:
    python setup.py
"""
from pathlib import Path

FILES = {}

FILES[".env.template"] = """DEEPSEEK_API_KEY=请替换为你的API_KEY
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
"""

FILES["requirements.txt"] = """browser-use>=0.1.40
playwright>=1.45
python-dotenv>=1.0
"""

FILES["install.bat"] = r"""@echo off
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

:: 激活并安装依赖
call venv\Scripts\activate.bat
echo [*] 安装 browser-use + Playwright (约需3分钟)...
pip install browser-use playwright python-dotenv -q
echo [✓] browser-use 安装完成

:: 安装 Chromium
echo [*] 安装 Chromium 浏览器 (首次约150MB)...
playwright install chromium
echo [✓] Chromium 安装完成

:: 创建 .env
if not exist .env copy .env.template .env

echo.
echo =====================================
echo   安装完成！
echo.
echo   下一步:
echo   1. 编辑 .env 填入 DeepSeek API Key
echo      (获取: https://platform.deepseek.com/api_keys)
echo   2. 命令行运行: venv\Scripts\activate.bat
echo   3. 首次: python login.py
echo   4. 之后每次: python main.py
echo =====================================
pause
"""

FILES["main.bat"] = r"""@echo off
chcp 65001 >nul
call venv\Scripts\activate.bat
python main.py
pause
"""

FILES["login.py"] = r'''"""
演出经纪人继续教育 — 登录脚本
运行后浏览器会打开登录页，请手动输入账号密码和验证码。
登录成功后自动保存 cookies，关闭浏览器即可。
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

TOKEN_URL = "https://zxpx.mr.mct.gov.cn/login.html?system_type=bookingagent&token=mSskz5o23t8O81MtNSZa"
AUTH_FILE = Path(__file__).parent / "auth.json"

def main():
    print("正在打开登录页面...")
    print("请在浏览器中输入账号、密码和验证码完成登录")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized"],
        )
        context = browser.new_context(
            viewport={"width": 1400, "height": 900},
            locale="zh-CN",
        )
        page = context.new_page()

        page.goto(TOKEN_URL, wait_until="networkidle", timeout=30000)

        current_url = page.url
        if "/member/" in current_url or "/system/" in current_url:
            print("✓ Token 自动登录成功！无需手动输入")
        else:
            print("⚠ 需要手动登录（已弹出验证码）")
            print("请在浏览器中完成登录，然后回到这里按 Enter...")
            input()

            try:
                page.wait_for_url("**/member/**", timeout=60000)
                print("✓ 检测到登录成功！")
            except:
                current_url = page.url
                if "/member/" in current_url or "/system/" in current_url:
                    print("✓ 登录成功！")
                else:
                    print("✗ 未检测到登录跳转，将保存当前状态")

        context.storage_state(path=str(AUTH_FILE))
        print(f"✓ 登录状态已保存到: {AUTH_FILE}")
        browser.close()

    print()
    print("接下来运行 main.py 即可开始自动刷课！")

if __name__ == "__main__":
    main()
'''

FILES["main.py"] = r'''"""
演出经纪人继续教育 — 自动刷课脚本
需要先运行 login.py 保存登录状态。
"""
import asyncio
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from browser_use import Agent, Browser, BrowserProfile, ChatOpenAI

load_dotenv()

TARGET_URL = "https://zxpx.mr.mct.gov.cn"
AUTH_FILE = Path(__file__).parent / "auth.json"

TASK = f"""
请完成以下刷课任务，全程用中文理解和操作：

1. 先打开 {TARGET_URL}/member/ 页面
2. 在这个页面找到和「课程」「继续教育」「在线学习」「我的课程」相关的入口，点击进去
3. 找到第一个状态不是「已完成」的课程，点进去开始学习
4. 进入课程播放页面后：
   - 找到播放按钮并点击开始播放
   - 视频播放期间，每1分钟左右检查一下有没有弹出「继续学习」「确认」「我知道了」之类的弹窗，有就点掉
   - 不要快进，让视频正常播放
5. 当视频播放完毕（进度条到100%或者出现下一节按钮），点击下一节
6. 重复步骤4-5，直到这门课所有小节都显示完成
7. 如果还有别的未完成课程，回到课程列表重复步骤3-6
8. 全部完成后告诉我

重要提醒：
- 视频播放时不要提前点下一节
- 弹窗必须处理否则视频会暂停
- 如果遇到验证码或报错页面，停下来告诉我
"""

async def main():
    if not AUTH_FILE.exists():
        print("✗ 未找到登录状态文件 auth.json")
        print("请先运行: python login.py")
        return

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key or api_key == "请替换为你的API_KEY":
        print("✗ 请在 .env 文件中设置正确的 DEEPSEEK_API_KEY")
        print("获取地址: https://platform.deepseek.com/api_keys")
        print("新用户免费赠送 500万 token")
        return

    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

    with open(AUTH_FILE) as f:
        storage_state = json.load(f)

    print("🚀 启动浏览器，开始自动刷课...")
    print("💡 浏览器窗口会显示操作过程，可以围观")
    print("💡 如果卡住了，关闭窗口重新来\n")

    browser = Browser(
        browser_profile=BrowserProfile(
            storage_state=storage_state,
            headless=False,
            window_size={"width": 1400, "height": 900},
        ),
    )

    agent = Agent(
        task=TASK,
        llm=ChatOpenAI(
            model="deepseek-chat",
            base_url=base_url,
            api_key=api_key,
        ),
        browser=browser,
        use_vision=True,
    )

    try:
        result = await agent.run()
        print("\n" + "=" * 50)
        print("📋 任务完成！")
        print(result)
    except KeyboardInterrupt:
        print("\n⚠ 用户手动中断")
    except Exception as e:
        print(f"\n✗ 运行出错: {e}")

if __name__ == "__main__":
    asyncio.run(main())
'''


def main():
    base = Path("bookingagent-course-bot")
    base.mkdir(exist_ok=True)

    for filename, content in FILES.items():
        filepath = base / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.lstrip("\n"))
        print(f"✓ {filepath}")

    print(f"\n完成！共创建 {len(FILES)} 个文件")
    print("下一步: 进入 bookingagent-course-bot 目录，双击 install.bat")


if __name__ == "__main__":
    main()
