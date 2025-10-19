import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

required_packages = [
    "PyQt5",
    "mysql-connector-python"
]

for pkg in required_packages:
    try:
        install(pkg)
        print(f"✅ Installed: {pkg}")
    except Exception as e:
        print(f"❌ Failed to install {pkg}: {e}")