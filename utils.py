# "socks5://2d00022f5a3e03595900:85166abe4db694dd@gw.dataimpulse.com:824"
import requests
import random
from fake_useragent import UserAgent
import string
import re

# Inisialisasi UserAgent
ua = UserAgent(browsers=['chrome', 'edge'])

def generate_session_id(length=4):
    """Membuat ID sesi acak untuk DataImpulse Sticky Session."""
    return ''.join(random.choices(string.digits, k=length))

def get_random_user_agent(p):
    """
    Mengambil UA asli dari engine, lalu memodifikasi platform-nya.
    """
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    ua_asli = page.evaluate("navigator.userAgent")
    browser.close()
    
    # Ambil versi asli (misal: 96.0.4664.93)
    version_match = re.search(r"Chrome\/(\d+\.\d+\.\d+\.\d+)", ua_asli)
    chrome_version = "145.0.7632.6"

    platforms = [
        "Windows NT 10.0; Win64; x64",
        "Macintosh; Intel Mac OS X 10_15_7",
        "X11; Linux x86_64"
    ]
    selected_platform = random.choice(platforms)
    
    final_ua = f"Mozilla/5.0 ({selected_platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36"
    
    print(f"\n[UA_LOG] Engine Version : {chrome_version}")
    print(f"[UA_LOG] Platform       : {selected_platform}")
    print(f"[UA_LOG] Final UA Set   : {final_ua}\n")
    
    return final_ua

def get_proxy(session_id):
    """
    Format DataImpulse untuk Sticky Session:
    username;session.ID:password@host:port
    """
    base_user = "2d00022f5a3e03595900" # Ganti dengan username DataImpulse Anda
    password = "85166abe4db694dd"  # Ganti dengan password DataImpulse Anda
    host_port = "gw.dataimpulse.com:823" # Host standar DataImpulse
    
    # Perhatikan double underscore '__' sebelum session
    proxy_url = f"http://{base_user};sessid.{session_id}:{password}@{host_port}"
    print(proxy_url)
    return proxy_url

def get_ip_info(proxy_url=None):
    """Mendapatkan info timezone dan lokasi berdasarkan IP."""
    try:
        url = "http://ip-api.com/json/?fields=status,message,country,city,timezone,lat,lon,query"
        # Memerlukan pip install requests[socks]
        proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
        
        response = requests.get(url, proxies=proxies, timeout=15)
        return response.json()
    except Exception as e:
        print(f"[!] Gagal cek IP: {e}")
        return {"timezone": "UTC", "lat": 0, "lon": 0, "query": "127.0.0.1"}