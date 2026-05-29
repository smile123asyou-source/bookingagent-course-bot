"""
演出经纪人继续教育 — 登录脚本 (保存 cookies)
运行后浏览器会打开登录页，请手动输入账号密码和验证码。
登录成功后自动保存，关闭浏览器即可。
"""
import os
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
        # 启动 Chromium（显示窗口，让阿阳可以看到并操作）
        browser = p.chromium.launch(
            headless=False,  # 显示浏览器窗口
            args=["--start-maximized"],
        )
        context = browser.new_context(
            viewport={"width": 1400, "height": 900},
            locale="zh-CN",
        )
        page = context.new_page()

        # 打开 token 登录链接
        page.goto(TOKEN_URL, wait_until="networkidle", timeout=30000)

        # 检测是否自动登录成功
        # 如果页面 URL 跳转到 /member/ 或 /system/ 说明自动登录了
        current_url = page.url
        if "/member/" in current_url or "/system/" in current_url:
            print("✅ Token 自动登录成功！无需手动输入")
        else:
            print("⚠️  需要手动登录（已弹出验证码）")
            print("请在浏览器中完成登录，然后回到这里按 Enter...")
            input()

            # 等待用户登录后页面跳转
            try:
                page.wait_for_url("**/member/**", timeout=60000)
                print("✅ 检测到登录成功！")
            except:
                # 可能跳转到了 /system/
                current_url = page.url
                if "/member/" in current_url or "/system/" in current_url:
                    print("✅ 登录成功！")
                else:
                    print("❌ 未检测到登录跳转，将保存当前状态")

        # 保存浏览器状态（cookies + localStorage）
        context.storage_state(path=str(AUTH_FILE))
        print(f"✅ 登录状态已保存到: {AUTH_FILE}")

        browser.close()

    print()
    print("接下来运行 main.py 即可开始自动刷课！")

if __name__ == "__main__":
    main()
