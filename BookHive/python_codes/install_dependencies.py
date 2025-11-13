"""
Dependency Installation Module

This module handles the installation of required Python packages for the BookHive application.
It uses pip to install PyQt5 for the GUI and mysql-connector-python for database connectivity.
"""

import subprocess
import sys

def install(package):
    """
    Install a Python package using pip.

    Args:
        package (str): Name of the package to install
    """
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# List of required packages for the application
required_packages = [
    "PyQt5",  # GUI framework for the application interface
    "mysql-connector-python==9.4.0",  # MySQL database connector (pinned to working version)
    "bcrypt"  # Password hashing library
]

# Attempt to install each required package
for pkg in required_packages:
    try:
        install(pkg)
        print(f"✅ Installed: {pkg}")
    except Exception as e:
        print(f"❌ Failed to install {pkg}: {e}")
