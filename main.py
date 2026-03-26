    # TARGET_URL = "https://amiunique.org/fingerprint" # Ganti dengan landing page tujuan
    # TARGET_URL = "https://browserleaks.com/webrtc" # Ganti dengan landing page tujuan
    # TARGET_URL = "https://champagnegood22.blogspot.com/" # Ganti dengan landing page tujuan

from browser_logic import run_visit, run_fingerprintcheck
from utils import generate_session_id
import sys
if __name__ == "__main__":
    TARGET_URL = "https://chamberforgood5.blogspot.com/"
    FINGERPRINT_SCORE_MIN = 82
    use_proxy = True

    while True:
        # --- SESSION DIHANDLE DI SINI ---
        session_id = generate_session_id() if use_proxy else "default"

        # score = run_fingerprintcheck(
        #     use_proxy=use_proxy,
        #     session_id=session_id
        # )

        # print("[!] Fingerprint Score: ", score)
        
        # if(score < FINGERPRINT_SCORE_MIN):
        #     print("[!] Fingerprint Score too low! aborted.")
        #     continue

        run_visit(
            TARGET_URL,
            use_proxy=use_proxy,
            session_id=session_id)
