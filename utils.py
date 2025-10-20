import requests

def fetch_ip() -> str:
    """通过api获取宿主机当前的IP地址"""
    url: str = "https://ipv4.icanhazip.com"
    try:
        resp = requests.get(url, timeout=5)
    except requests.Timeout as e:
        raise RuntimeError("Request timeout") from e
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}")
    ip = resp.text.strip()
    if not _is_ipv4(ip):
        raise RuntimeError("返回格式不是合法 IPv4")
    return ip

def _is_ipv4(addr: str) -> bool:
    """判断是否是合法的 IPv4 地址"""
    try:
        parts = addr.split(".")
        return len(parts) == 4 and all(0 <= int(p) <= 255 for p in parts)
    except Exception:
        return False