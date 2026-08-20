import asyncio
import json
import random
import time
from pathlib import Path
import pyotp
from playwright.async_api import async_playwright
from typing import Optional
import time as _time

from .twofa import create_twofa_session, get_twofa_status

LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

async def human_type(page, selector: str, text: str, min_delay=50, max_delay=150):
    for ch in text:
        await page.type(selector, ch, delay=random.randint(min_delay, max_delay))

async def human_mouse_move(page, start, end, steps=10):
    sx, sy = start
    ex, ey = end
    for i in range(steps):
        nx = sx + (ex - sx) * (i + 1) / steps + random.uniform(-2, 2)
        ny = sy + (ey - sy) * (i + 1) / steps + random.uniform(-2, 2)
        await page.mouse.move(nx, ny)
        await asyncio.sleep(random.uniform(0.01, 0.05))

async def connect_cdp_and_run(cdp_ws: str, cookies_path: Optional[str], proxy=None, twofa_secret: Optional[str]=None, account_login: Optional[str]=None, account_password: Optional[str]=None, account_id: Optional[int]=None):
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp(cdp_ws)
    context = await browser.new_context()
    if cookies_path:
        try:
            with open(cookies_path, "r") as f:
                cookies = json.load(f)
            await context.add_cookies(cookies)
        except Exception:
            pass
    page = await context.new_page()
    try:
        await page.goto("https://m.facebook.com", timeout=30000)
        # if login form present
        login_input = await page.query_selector("input[name='email']")
        if login_input:
            if account_login and account_password:
                await page.fill("input[name='email']", "")
                await human_type(page, "input[name='email']", account_login)
                await human_type(page, "input[name='pass']", account_password)
                # click login
                btn = await page.query_selector("button[name='login']")
                if btn:
                    await btn.click()
                await asyncio.sleep(5)
                # handle 2FA
                if await page.query_selector("input[name='approvals_code']"):
                    # create 2FA session so user can input code manually via web
                    if account_id:
                        tf = create_twofa_session(account_id)
                        token = tf['token']
                        url = tf['url']
                        print(f"2FA required for account {account_id}. Visit: {url}")
                        # poll for code
                        code = None
                        timeout = 300
                        interval = 3
                        waited = 0
                        while waited < timeout:
                            s = get_twofa_status(token)
                            if s and s.get('code'):
                                code = s.get('code')
                                break
                            await asyncio.sleep(interval)
                            waited += interval
                        if code:
                            await human_type(page, "input[name='approvals_code']", code)
                            sub = await page.query_selector("button[type='submit']")
                            if sub:
                                await sub.click()
                            await asyncio.sleep(5)
                        else:
                            # timeout waiting for user input
                            raise Exception("2FA timeout waiting for user code")
                    else:
                        # fallback to TOTP if secret provided
                        if twofa_secret:
                            otp = pyotp.TOTP(twofa_secret).now()
                            await human_type(page, "input[name='approvals_code']", otp)
                            sub = await page.query_selector("button[type='submit']")
                            if sub:
                                await sub.click()
                            await asyncio.sleep(5)
        # dump cookies and localStorage
        cookies = await context.cookies()
        sessions_dir = Path("sessions")
        sessions_dir.mkdir(exist_ok=True)
        with open(sessions_dir / f"cookies_{int(time.time())}.json", "w") as f:
            json.dump(cookies, f)
        # diagnostics
        await page.screenshot(path=str(LOGS_DIR / f"screenshot_{int(time.time())}.png"), full_page=True)
        html = await page.content()
        with open(LOGS_DIR / f"dom_{int(time.time())}.html", "w", encoding="utf-8") as f:
            f.write(html)
        return True
    except Exception as e:
        # capture on error
        try:
            await page.screenshot(path=str(LOGS_DIR / f"error_{int(time.time())}.png"), full_page=True)
        except Exception:
            pass
        with open(LOGS_DIR / f"error_{int(time.time())}.txt", "w") as f:
            f.write(str(e))
        return False
    finally:
        await context.close()
        await browser.close()
        await p.stop()
