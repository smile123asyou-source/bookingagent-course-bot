"""
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
        print("❌ 未找到登录状态文件 auth.json")
        print("请先运行: python login.py")
        return

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key or api_key == "请替换为你的API_KEY":
        print("❌ 请在 .env 文件中设置正确的 DEEPSEEK_API_KEY")
        print("获取地址: https://platform.deepseek.com/api_keys")
        print("新用户免费赠送 500万 token，刷完全部课估计只花几毛钱")
        return

    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

    # 加载登录状态（cookies + localStorage）
    with open(AUTH_FILE) as f:
        storage_state = json.load(f)

    print("🚀 启动浏览器，开始自动刷课...")
    print("💡 浏览器窗口会显示操作过程，阿阳可以围观")
    print("💡 如果卡住了，关闭这个窗口重新运行 login.py → main.py\n")

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
        print("\n⚠️ 用户手动中断")
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")

if __name__ == "__main__":
    asyncio.run(main())
