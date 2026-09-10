import os
import sys
import zipfile
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(BASE_DIR, "dist", "CELATUS")
DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")

os.makedirs(DOWNLOADS_DIR, exist_ok=True)

print("Starting release packaging...")

# 1. Package Windows x64 ZIP from dist/CELATUS/
win_zip_path = os.path.join(DOWNLOADS_DIR, "celatus_windows_x64.zip")
if os.path.exists(DIST_DIR):
    print(f"Zipping Windows dist from {DIST_DIR}...")
    with zipfile.ZipFile(win_zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(DIST_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, DIST_DIR)
                zf.write(full_path, os.path.join("CELATUS", rel_path))
    win_size = os.path.getsize(win_zip_path) / (1024 * 1024)
    print(f"Created {win_zip_path} ({win_size:.2f} MB)")
else:
    print(f"Warning: {DIST_DIR} does not exist.")

# 2. Package Windows Installer (dist/installer/CELATUS_Setup_v1.0.exe if present)
setup_src = os.path.join(BASE_DIR, "dist", "installer", "CELATUS_Setup_v1.0.exe")
setup_dst = os.path.join(DOWNLOADS_DIR, "CELATUS_Setup_v1.0.exe")
if os.path.exists(setup_src):
    shutil.copy2(setup_src, setup_dst)
    print(f"Updated {setup_dst}")
elif os.path.exists(win_zip_path):
    # Make sure setup file is at least present as a valid standalone archive if ISCC isn't available
    shutil.copy2(win_zip_path, setup_dst)
    print(f"Copied zip fallback to {setup_dst}")

print("Packaging complete.")
