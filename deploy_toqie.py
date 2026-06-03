# ====================================================================
# TOQIE RUNTIME GOVERNANCE PROTOCOL v1.0.0
# COPYRIGHT (C) 2026 THE BUILDER / ALL RIGHTS RESERVED
# PROVENANCE: CYBERNETIC NOISE RENORMALIZATION CORE
# AUTHORSHIP TYPE: SINGLE-ARCHITECT SIGNATURE RECORDED LUR-01
# ====================================================================
import os
import time

HIPPOCAMPUS_PATH = "private/kernel_hippocampus.py"

REQUIRED_PUBLIC_FILES = [
    "release/kernel_runner.py",
    "release/kernel_parser.py",
    "release/kernel_http.py",
    "release/kernel_secret_guard.py",
]

def verify_public_assets():
    missing = []
    for path in REQUIRED_PUBLIC_FILES:
        if not os.path.exists(path):
            missing.append(path)
    return missing

def boot_sequence():
    print()
    print("[SYSTEM BOOT] Initializing Toqie Kernel v1.0.0 Public Gatekeeper...")
    time.sleep(0.25)
    print("[CHECK] Verifying Public Release Assets...")
    time.sleep(0.25)

    missing = verify_public_assets()
    if missing:
        print("[FAIL] Public Kernel Assets Missing.")
        for path in missing:
            print(" - " + path)
        raise SystemExit(1)

    print("[PASS] Public Kernel Assets Verified.")
    print()

    if os.path.exists(HIPPOCAMPUS_PATH):
        print("[PRIVATE TRACK DETECTED] Hippocampus available.")
        print("MODE: ARCHITECT")
        print("HIPPOCAMPUS: ONLINE")
        print("PAIN LOGIC: ACTIVE")
    else:
        print("[PUBLIC TRACK] Community / Stateless Mode")
        print("WARNING: Hippocampus not included.")
        print("STATUS: No long-term friction memory. Repeated errors may loop.")

    print()
    print("[SYSTEM READY] Public release boot check complete.")

if __name__ == "__main__":
    boot_sequence()
