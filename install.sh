#!/bin/bash

# ============================================
# INSTALL SCRIPT FOR TALKER
# Piper TTS + SoX
# Tested on Ubuntu 24.04
# ============================================

set -e  # Exit immediately if a command fails

echo "============================================"
echo "        Installing Talker Dependencies"
echo "============================================"

# ---- Update system ----

echo "[1/3] Updating system packages..."
sudo apt update

# ---- Install dependencies ----

echo "[2/3] Installing required dependencies..."
sudo apt install -y \
    sox \
    libsox-fmt-all \
    alsa-utils

# ---- Verification ----

echo "[3/3] Verifying installation..."

if command -v sox >/dev/null 2>&1; then
    echo "SoX installed successfully:"
    sox --version
else
    echo "ERROR: SoX installation failed."
    exit 1
fi

echo ""

if command -v aplay >/dev/null 2>&1; then
    echo "ALSA utilities installed successfully."
else
    echo "WARNING: ALSA utilities were not found."
fi

echo "============================================"
echo "      TALKER DEPENDENCIES INSTALLED"
echo "============================================"