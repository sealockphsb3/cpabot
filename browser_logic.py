import time
import random
import re
import os
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
# Pastikan fungsi-fungsi ini tersedia di file utils Anda
from utils import get_random_user_agent, get_proxy, get_ip_info, generate_session_id

def get_locale_from_country(country_code):
    """Memetakan kode negara ke locale bahasa yang sesuai."""
    mapping = {
        'ID': 'id-ID', 'US': 'en-US', 'GB': 'en-GB', 'DE': 'de-DE',
        'FR': 'fr-FR', 'JP': 'ja-JP', 'KR': 'ko-KR', 'RU': 'ru-RU',
        'BR': 'pt-BR', 'ES': 'es-ES', 'IT': 'it-IT', 'MY': 'ms-MY',
        'SG': 'en-SG', 'TH': 'th-TH', 'VN': 'vi-VN'
    }
    return mapping.get(country_code.upper(), 'en-US')

def run_visit(url, use_proxy=False):
    # --- 1. Konfigurasi Path Profile (Simpan Cache) ---
    # Menggunakan folder lokal 'browser_profile' untuk menyimpan cache & session data
    user_data_dir = os.path.join(os.getcwd(), "browser_profile")

    with sync_playwright() as p:
        # --- 2. Inisialisasi Proxy & Session ---
        session_id = generate_session_id() if use_proxy else "default"
        proxy_raw = get_proxy(session_id) if use_proxy else None

        # --- 3. Ambil info IP (Lokasi, TZ, Country) ---
        ip_data = get_ip_info(proxy_raw)
        target_tz = ip_data.get('timezone', 'UTC')
        current_ip = ip_data.get('query', 'Unknown')
        country_code = ip_data.get('countryCode', 'US')
        target_locale = get_locale_from_country(country_code)
        
        # --- 4. Penanganan Proxy Auth untuk Persistent Context ---
        launch_proxy = None
        if use_proxy and proxy_raw:
            pattern = r"http://(?P<user>.*):(?P<pass>.*)@(?P<host>.*):(?P<port>\d+)"
            match = re.match(pattern, proxy_raw)
            if match:
                launch_proxy = {
                    "server": f"http://{match.group('host')}:{match.group('port')}",
                    "username": match.group('user'),
                    "password": match.group('pass')
                }
            else:
                launch_proxy = {"server": proxy_raw}

        # --- 5. Launch Persistent Context (Bukan Browser Biasa) ---
        # launch_persistent_context menggabungkan launch browser dan pembuatan context
        custom_ua = get_random_user_agent(p)
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            proxy=launch_proxy,
            user_agent=custom_ua,
            timezone_id=target_tz,
            locale=target_locale,
            geolocation={
                "latitude": ip_data.get('lat', 0), 
                "longitude": ip_data.get('lon', 0)
            },
            permissions=["geolocation"],
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--disable-quic",
                "--disable-http2",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                # Mematikan WebRTC sepenuhnya (Cara paling aman)
                "--enforce-webrtc-ip-permission-check",
                "--force-webrtc-ip-handling-policy=disable_non_proxied_udp" 
            ],
            viewport=None # None jika ingin mengikuti --start-maximized
        )
        context.add_init_script("""
            delete window.RTCPeerConnection;
            delete window.webkitRTCPeerConnection;
            delete window.RTCDataChannel;
            delete window.RTCIceGatherer;
        """)
        
        # --- 6. FITUR: KOSONGKAN COOKIES TIAP SESI ---
        # Cache tetap tersimpan di user_data_dir, tapi cookies dihapus agar dianggap user baru
        context.clear_cookies()
        
        page = context.new_page()
        stealth_sync(page)

        try:
            print(f"\n" + "="*50)
            print(f"[*] PROFILE DIR    : {user_data_dir}")
            print(f"[*] SESSION ID     : {session_id}")
            print(f"[*] TARGET URL     : {url}")
            print(f"[*] ACTION         : Cookies Cleared, Cache Retained")
            
            page.goto(url, wait_until="networkidle", timeout=60000)

            # --- 7. LOG VALIDASI ---
            browser_tz = page.evaluate("Intl.DateTimeFormat().resolvedOptions().timeZone")
            browser_lang = page.evaluate("navigator.language")
            
            print("-" * 50)
            print(f"[LOG] IP Address       : {current_ip}")
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
            print("="*50 + "\n")

            time.sleep(150) 
            
        except Exception as e:
            print(f"[!] Error saat kunjungan: {e}")
        finally:
            # Pada persistent context, menutup context otomatis menutup browser
            context.close()