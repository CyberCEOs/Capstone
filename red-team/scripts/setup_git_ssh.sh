#!/usr/bin/env bash
# Helper to create/use an SSH key for Git operations and optionally switch remote to SSH.
# Usage:
#   chmod +x scripts/setup_git_ssh.sh
#   ./scripts/setup_git_ssh.sh   # interactive

set -euo pipefail

KEY_PATH_DEFAULT="$HOME/.ssh/capstone_github_id"
KEY_PATH="${1:-$KEY_PATH_DEFAULT}"

echo "[setup_git_ssh] Using key path: $KEY_PATH"

if [ -f "$KEY_PATH" ]; then
  echo "Found existing key: $KEY_PATH"
else
  echo "No key found at $KEY_PATH — generating a new ed25519 keypair (no passphrase)"
  ssh-keygen -t ed25519 -f "$KEY_PATH" -N "" -C "capstone@$(hostname)"
fi

PUBKEY="$KEY_PATH.pub"
echo
echo "=== Public key (copy this to your GitHub account -> Settings -> SSH and GPG keys) ==="
cat "$PUBKEY"
echo "================================================================"

echo
echo "Next steps (manual):"
echo "  1) Open https://github.com/settings/keys and add the public key above as a new SSH key."
echo "  2) After adding the key, press ENTER here to continue and test the SSH connection." 
read -r -p "Press ENTER after adding the key to GitHub..."

echo "Adding key to ssh-agent (starts agent if needed)..."
if [ -z "${SSH_AUTH_SOCK:-}" ]; then
  echo "Starting ssh-agent..."
  eval "$(ssh-agent -s)"
fi
ssh-add "$KEY_PATH" || true

echo "Testing connection to GitHub (this may prompt once for confirmation of host key)..."
if ssh -T git@github.com 2>&1 | sed -n '1,200p'; then
  echo "SSH to GitHub succeeded (or interactive welcome)."
fi

# Offer to convert origin remote to SSH
ORIGIN_URL=$(git remote get-url origin 2>/dev/null || true)
if [ -z "$ORIGIN_URL" ]; then
  echo "No 'origin' remote found in this repo. You can add one and re-run this script." 
  exit 0
fi

echo "Current origin: $ORIGIN_URL"
if echo "$ORIGIN_URL" | grep -qE '^https://'; then
  # Convert https URL to SSH form: https://github.com/owner/repo.git -> git@github.com:owner/repo.git
  SSH_URL=$(echo "$ORIGIN_URL" | sed -E 's#https://github.com/(.*)#git@github.com:\1#')
  echo "Proposed SSH origin: $SSH_URL"
  read -r -p "Replace origin with SSH URL? (y/N) " resp
  if [[ "$resp" =~ ^[Yy]$ ]]; then
    git remote set-url origin "$SSH_URL"
    echo "Updated origin to $SSH_URL"
  else
    echo "Leaving origin as-is. You can switch later with: git remote set-url origin <ssh-url>"
  fi
else
  echo "Origin already uses non-HTTPS (likely SSH). No change needed."
fi

echo "Testing git push (dry-run): git push --dry-run origin HEAD"
git push --dry-run origin HEAD || true

echo "Done — your repo should now be able to authenticate to GitHub via SSH. Try: git push origin HEAD"
