from browser_logic import run_visit

if __name__ == "__main__":
    # TARGET_URL = "https://amiunique.org/fingerprint" # Ganti dengan landing page tujuan
    # TARGET_URL = "https://browserleaks.com/webrtc" # Ganti dengan landing page tujuan
    # TARGET_URL = "https://www.browserscan.net/" # Ganti dengan landing page tujuan
    TARGET_URL = "https://champagnegood22.blogspot.com/" # Ganti dengan landing page tujuan
    
    # Menjalankan kunjungan
    run_visit(TARGET_URL, use_proxy=True) # Ubah ke True jika proxy sudah siap