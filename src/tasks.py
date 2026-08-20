from celery import Celery
import os
import asyncio
from .anti_detect_client import AntiDetectClient
from .proxy_check import check_proxy
from .session_manager import connect_cdp_and_run

CELERY_BROKER = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
ANTI_DETECT_BASE = os.getenv('ANTIDETECT_BASE', 'http://antidetect.local:35000')

app = Celery('fbfarm', broker=CELERY_BROKER)

@app.task(bind=True, max_retries=2)
def run_account_session(self, account_id, profile_spec, proxy_url, twofa_secret=None, account_login=None, account_password=None):
    async def _run():
        adc = AntiDetectClient(ANTI_DETECT_BASE)
        # create profile (or reuse)
        profile = await adc.create_profile(profile_spec)
        start_info = await adc.start_profile(profile.get('id'))
        cdp_ws = start_info.get('cdp_ws')
        ok, info = await check_proxy(proxy_url)
        if not ok:
            return {"ok": False, "reason": "proxy_bad", "info": info}
        ok2 = await connect_cdp_and_run(cdp_ws, cookies_path=None, proxy=proxy_url, twofa_secret=twofa_secret, account_login=account_login, account_password=account_password)
        # stop profile
        try:
            await adc.stop_profile(profile.get('id'))
        except Exception:
            pass
        return {"ok": ok2}
    return asyncio.run(_run())
