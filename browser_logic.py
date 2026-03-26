import os
import re
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

from utils import (
    get_random_user_agent,
    get_proxy,
    get_ip_info,
    generate_session_id
)


# =========================
# CONFIG & HELPERS
# =========================

def get_locale_from_country(country_code: str) -> str:
    mapping = {
        'ID': 'id-ID', 'US': 'en-US', 'GB': 'en-GB', 'DE': 'de-DE',
        'FR': 'fr-FR', 'JP': 'ja-JP', 'KR': 'ko-KR', 'RU': 'ru-RU',
        'BR': 'pt-BR', 'ES': 'es-ES', 'IT': 'it-IT', 'MY': 'ms-MY',
        'SG': 'en-SG', 'TH': 'th-TH', 'VN': 'vi-VN'
    }
    return mapping.get(country_code.upper(), 'en-US')


def parse_proxy(proxy_raw: str):
    """Handle proxy format (with / without auth)."""
    if not proxy_raw:
        return None

    pattern = r"http://(?P<user>.*):(?P<pass>.*)@(?P<host>.*):(?P<port>\d+)"
    match = re.match(pattern, proxy_raw)

    if match:
        return {
            "server": f"http://{match.group('host')}:{match.group('port')}",
            "username": match.group('user'),
            "password": match.group('pass')
        }

    return {"server": proxy_raw}


def build_browser_context(p, config: dict):
    """Create persistent browser context."""
    return p.chromium.launch_persistent_context(
        config["user_data_dir"],
        headless=False,
        proxy=config["proxy"],
        user_agent=config["user_agent"],
        timezone_id=config["timezone"],
        locale=config["locale"],
        geolocation=config["geolocation"],
        permissions=["geolocation"],
        args=[
            "--disable-blink-features=AutomationControlled",
            "--start-maximized",
            "--disable-quic",
            "--disable-http2",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--enforce-webrtc-ip-permission-check",
            "--force-webrtc-ip-handling-policy=disable_non_proxied_udp"
        ],
        viewport=None
    )


def apply_anti_detection(context):
    """Disable WebRTC leaks."""
    context.add_init_script("""
        delete window.RTCPeerConnection;
        delete window.webkitRTCPeerConnection;
        delete window.RTCDataChannel;
        delete window.RTCIceGatherer;
    """)


def log_environment(ip_data, browser_tz, browser_lang, target_tz, target_locale):
    print("-" * 50)
    print(f"[LOG] IP Address       : {ip_data.get('query')}")
    print(f"[LOG] Lokasi           : {ip_data.get('city')}, {ip_data.get('country')}")
    print(f"[LOG] Locale Target    : {target_locale}")
    print(f"[LOG] Locale Browser   : {browser_lang}")
    print(f"[LOG] Timezone Target  : {target_tz}")
    print(f"[LOG] Timezone Browser : {browser_tz}")
    print("-" * 50)

    if browser_tz.lower() == target_tz.lower():
        print("[RESULT] ✅ SINKRON: Timezone & Lokasi sesuai.")
    else:
        print("[RESULT] ⚠️ MISMATCH: Timezone berbeda!")


# =========================
# MAIN FUNCTION
# =========================
def run_fingerprintcheck(use_proxy: bool = False, session_id: str = "default"):
    user_data_dir = os.path.join(os.getcwd(), "browser_profile")
    url = "https://www.browserscan.net/"

    with sync_playwright() as p:
        # --- PROXY ---
        proxy_raw = get_proxy(session_id) if use_proxy else None
        proxy_config = parse_proxy(proxy_raw)

        # --- IP INFO ---
        ip_data = get_ip_info(proxy_raw)
        timezone = ip_data.get('timezone', 'UTC')
        country_code = ip_data.get('countryCode', 'US')
        locale = get_locale_from_country(country_code)

        config = {
            "user_data_dir": user_data_dir,
            "proxy": proxy_config,
            "user_agent": get_random_user_agent(p),
            "timezone": timezone,
            "locale": locale,
            "geolocation": {
                "latitude": ip_data.get('lat', 0),
                "longitude": ip_data.get('lon', 0)
            }
        }

        context = build_browser_context(p, config)
        apply_anti_detection(context)

        context.clear_cookies()

        page = context.new_page()
        stealth_sync(page)
        score = "-"
        try:
            print("\n" + "=" * 50)
            print(f"[*] PROFILE DIR : {user_data_dir}")
            print(f"[*] SESSION ID  : {session_id}")
            print(f"[*] TARGET URL  : {url}")
            print(f"[*] ACTION      : Cookies Cleared, Cache Retained")

            page.goto(url, wait_until="networkidle", timeout=60000)

            browser_tz = page.evaluate("Intl.DateTimeFormat().resolvedOptions().timeZone")
            browser_lang = page.evaluate("navigator.language")

            log_environment(ip_data, browser_tz, browser_lang, timezone, locale)

            page.wait_for_selector("#anchor_progress")
            text = page.locator("#anchor_progress").inner_text()
            match = re.search(r'(\d+)%', text)
            if match:
                score = int(match.group(1))
        except Exception as e:
            print(f"[!] Error saat kunjungan: {e}")

        finally:
            context.close()
            
        return score

def run_visit(url: str, use_proxy: bool = False, session_id: str = "default"):
    user_data_dir = os.path.join(os.getcwd(), "browser_profile")

    with sync_playwright() as p:
        # --- PROXY ---
        proxy_raw = get_proxy(session_id) if use_proxy else None
        proxy_config = parse_proxy(proxy_raw)

        # --- IP INFO ---
        ip_data = get_ip_info(proxy_raw)
        timezone = ip_data.get('timezone', 'UTC')
        country_code = ip_data.get('countryCode', 'US')
        locale = get_locale_from_country(country_code)

        config = {
            "user_data_dir": user_data_dir,
            "proxy": proxy_config,
            "user_agent": get_random_user_agent(p),
            "timezone": timezone,
            "locale": locale,
            "geolocation": {
                "latitude": ip_data.get('lat', 0),
                "longitude": ip_data.get('lon', 0)
            }
        }

        context = build_browser_context(p, config)
        apply_anti_detection(context)

        context.clear_cookies()

        page = context.new_page()
        stealth_sync(page)

        try:
            page.goto(url, timeout=60000)

            browser_tz = page.evaluate("Intl.DateTimeFormat().resolvedOptions().timeZone")
            browser_lang = page.evaluate("navigator.language")

            log_environment(ip_data, browser_tz, browser_lang, timezone, locale)

            page.wait_for_selector("#Image1")
            page.locator("#Image1").click(position={"x": 20, "y": 15})
            time.sleep(3)
            page.wait_for_load_state("domcontentloaded")
            time.sleep(30)
        except Exception as e:
            print(f"[!] Error saat kunjungan: {e}")

        finally:
            context.close()