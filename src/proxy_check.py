import httpx
from typing import Optional, Tuple

async def check_proxy(proxy_url: str, geo_country: Optional[str] = None, timeout: int = 8) -> Tuple[bool, dict]:
    """
    proxy_url example: "http://user:pass@host:port" or "socks5://host:port"
    returns (ok, info)
    info contains ip and geo (from ip-api)
    """
    async with httpx.AsyncClient(proxies=proxy_url, timeout=timeout) as client:
        try:
            r = await client.get("https://api.ipify.org?format=json")
            r.raise_for_status()
            ip = r.json().get("ip")
            geo = {}
            if ip:
                g = await client.get(f"http://ip-api.com/json/{ip}")
                geo = g.json()
                if geo_country and geo.get("countryCode") != geo_country:
                    return False, {"ip": ip, "geo": geo}
            return True, {"ip": ip, "geo": geo}
        except Exception as e:
            return False, {"error": str(e)}
