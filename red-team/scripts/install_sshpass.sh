#!/usr/bin/env bash
# Install sshpass on macOS (Homebrew) or Debian/Ubuntu (apt).
# Usage: sudo ./install_sshpass.sh  # may need sudo for apt

set -euo pipefail

if command -v sshpass >/dev/null 2>&1; then
  echo "sshpass is already installed: $(command -v sshpass)"
  exit 0
fi

echo "sshpass not found. Attempting automated install..."

if command -v brew >/dev/null 2>&1; then
  echo "Detected Homebrew. Installing sshpass via brew..."
  # Use known taps that provide sshpass
  if brew install hudochenkov/sshpass/sshpass >/dev/null 2>&1; then
    echo "sshpass installed via Homebrew."
    exit 0
  fi
  if brew install esolitos/sshpass/sshpass >/dev/null 2>&1; then
    echo "sshpass installed via Homebrew (esolitos)."
    exit 0
  fi
  echo "Homebrew install attempt failed. You may need to run 'brew install hudochenkov/sshpass/sshpass' manually."
  exit 2
fi

if command -v apt-get >/dev/null 2>&1; then
  echo "Detected apt-get. Installing sshpass via apt-get..."
  sudo apt-get update
  sudo apt-get install -y sshpass
  echo "sshpass installed via apt-get."
  exit 0
fi

if command -v yum >/dev/null 2>&1; then
  echo "Detected yum. Installing sshpass via yum..."
  sudo yum install -y epel-release || true
  sudo yum install -y sshpass
  echo "sshpass installed via yum."
  exit 0
fi

echo "Automatic installation not supported on this platform."
echo "Please install sshpass manually. On macOS with Homebrew try:"
echo "  brew install hudochenkov/sshpass/sshpass"
echo "On Debian/Ubuntu:"
echo "  sudo apt-get update && sudo apt-get install -y sshpass"
exit 3
