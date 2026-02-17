#!/bin/env bash
set -euo pipefail

echo "============================================================"
echo " Installing Mimic3 TTS (offline) + en_US/ljspeech_low voice"
echo "============================================================"

# -----------------------------
# 1) System dependencies
# -----------------------------
echo "[1/5] Installing system packages..."
sudo apt update
sudo apt install -y \
  git \
  pipx \
  alsa-utils

# Make sure pipx binaries are on PATH for future shells
pipx ensurepath >/dev/null || true

# Add pipx path for THIS shell session too (so mimic3 works immediately)
export PATH="$HOME/.local/bin:$PATH"

# -----------------------------
# 2) Install Mimic3 via pipx
# -----------------------------
echo "[2/5] Installing Mimic3 (mycroft-mimic3-tts) via pipx..."
if pipx list | grep -q "mycroft_mimic3_tts"; then
  echo "  - Mimic3 already installed via pipx."
else
  pipx install mycroft-mimic3-tts
fi

# -----------------------------
# 3) Compatibility fix (pkg_resources)
# -----------------------------
echo "[3/5] Pinning setuptools<81 for epitran/pkg_resources compatibility..."
pipx runpip mycroft-mimic3-tts install -U "setuptools<81" >/dev/null

# -----------------------------
# 4) Download voice for offline usage
# -----------------------------
echo "[4/5] Downloading voice: en_US/ljspeech_low ..."
# If already present, mimic3-download will typically skip/reuse cached files
mimic3-download "en_US/ljspeech_low" || {
  echo "  - mimic3-download failed. Listing voices for troubleshooting:"
  mimic3 --voices || true
  exit 1
}

# -----------------------------
# 5) Quick audio test
# -----------------------------
echo "[5/5] Quick test (will play audio)..."
mimic3 --voice "en_US/ljspeech_low" --length-scale 0.90 --noise-w 0.80 --noise-scale 0.60 \
  --stdout "Hello. Mimic three installation successful." | aplay -q

echo "============================================================"
echo " Done!"
echo " - Mimic3 CLI: $(command -v mimic3)"
echo " - Voice installed: en_US/ljspeech_low"
echo "============================================================"
echo ""
echo "If 'mimic3' is not found in a new terminal, run:"
echo "  echo 'export PATH=\$HOME/.local/bin:\$PATH' >> ~/.zshrc"
echo "  source ~/.zshrc"
