#!/bin/bash

# ============================================
#  INSTALL SCRIPT FOR FLITE (Festival Lite)
#  Tested on Ubuntu 22.04 / 24.04
#  Author: Vero
# ============================================

set -e  # Exit on error

echo "============================================"
echo "     Installing FLITE (Festival Lite)"
echo "============================================"

# ---- Update system ----
echo "[1/5] Updating system..."
sudo apt update -y

# ---- Install dependencies ----
echo "[2/5] Installing required dependencies..."
sudo apt install -y build-essential git automake autoconf libtool

# ---- Clone or update Flite ----
echo "[3/5] Downloading Flite from official repository..."

if [ ! -d "flite" ]; then
    git clone https://github.com/festvox/flite.git
else
    echo "Flite folder already exists. Updating..."
    cd flite && git pull && cd ..
fi

# ---- Build flite ----
echo "[4/5] Building Flite..."
cd flite
./configure
make -j$(nproc)

# ---- Optional: install system-wide ----
echo "[5/5] Installing system-wide..."
sudo make install

cd ..

echo "============================================"
echo "          FLITE INSTALLED SUCCESSFULLY"
echo "============================================"

# ---- Verification ----
echo "Testing flite..."
flite -t "Flite has been installed correctly."

echo "Done!"
