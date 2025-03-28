import subprocess
import sys


def check_vlc_installed() -> bool:
    """Check if VLC is installed on the system."""
    platform = sys.platform

    if platform == "darwin":
        try:
            subprocess.run(["brew", "list", "vlc"], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            print("VLC not found. Please install it using: brew install vlc")
            return False
    elif platform == "linux":
        try:
            subprocess.run(["vlc", "--version"], check=True, capture_output=True)
            return True
        except FileNotFoundError:
            print("VLC not found. Please install it using your package manager:")
            print("Ubuntu/Debian: sudo apt install vlc")
            print("Fedora: sudo dnf install vlc")
            return False
    return False
