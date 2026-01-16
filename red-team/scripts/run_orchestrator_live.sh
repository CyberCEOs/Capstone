#!/usr/bin/env bash
# Wrapper to prepare SSH auth and run the red-team orchestrator in LIVE mode.
# - Loads private key into ssh-agent (uses add_ssh_key_to_agent.sh)
# - Exports sensible defaults for Kali SSH and target variables (overridable via env)
# - Unsets docker-exec routing so the agents use SSH to the Kali host

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# If a .env.live file is present in the red-team directory, source it to
# load environment variables (convenient for automation). Example .env.live:
#   KALI_SSH_KEY=~/.ssh/id_ed25519
#   KALI_SSH_KEY_PASSPHRASE=your_passphrase_here
#   KALI_SSH_HOST=localhost
#   KALI_SSH_PORT=2222
#   TARGET_IP=192.168.4.50
ENV_FILE="$ROOT_DIR/.env.live"
if [ -f "$ENV_FILE" ]; then
  echo "[run_orchestrator_live] Sourcing env file $ENV_FILE"
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

# Defaults (can be overridden in the environment or via .env.live)
KALI_SSH_HOST="${KALI_SSH_HOST:-localhost}"
KALI_SSH_PORT="${KALI_SSH_PORT:-2222}"
KALI_SSH_USER="${KALI_SSH_USER:-pentester}"
KALI_SSH_KEY="${KALI_SSH_KEY:-$HOME/.ssh/id_ed25519}"
KALI_SSH_KEY_PASSPHRASE="${KALI_SSH_KEY_PASSPHRASE:-}"
KALI_SSH_PASS="${KALI_SSH_PASS:-}"
TARGET_IP="${TARGET_IP:-192.168.4.50}"
TARGET_SSH_USER="${TARGET_SSH_USER:-root}"
TARGET_SSH_PASS="${TARGET_SSH_PASS:-toor}"

export LIVE_MODE=1
export KALI_SSH_HOST KALI_SSH_PORT KALI_SSH_USER KALI_SSH_KEY KALI_SSH_KEY_PASSPHRASE KALI_SSH_PASS
export TARGET_IP TARGET_SSH_USER TARGET_SSH_PASS

# Ensure we use SSH path (not docker-exec)
unset KALI_DOCKER_CONTAINER || true

if [ "$(id -u)" -eq 0 ]; then
  echo "[run_orchestrator_live] WARNING: running as root (sudo)."
  echo "It's recommended to run this script as your regular user so ssh-agent and keys are available." 
  echo "If you must run as root, ensure SSH_AUTH_SOCK is forwarded (export SSH_AUTH_SOCK before sudo)."
fi

echo "[run_orchestrator_live] Preparing SSH agent and keys..."

# Add private key to ssh-agent. The helper will start the agent if needed.
if [ -n "${KALI_SSH_KEY_PASSPHRASE:-}" ]; then
  KALI_SSH_KEY_PASSPHRASE="$KALI_SSH_KEY_PASSPHRASE" "$SCRIPT_DIR/add_ssh_key_to_agent.sh" "$KALI_SSH_KEY"
else
  "$SCRIPT_DIR/add_ssh_key_to_agent.sh" "$KALI_SSH_KEY"
fi

echo "[run_orchestrator_live] SSH key loaded. Verifying agent identities:"
ssh-add -l || true

echo "[run_orchestrator_live] Running orchestrator (LIVE_MODE=1) against $TARGET_IP"
cd "$ROOT_DIR"
python3 agents/orchestrator.py
