#!/usr/bin/env bash
# Add a private SSH key to the local ssh-agent.
# Usage:
#   KALI_SSH_KEY_PASSPHRASE=yourpass ./add_ssh_key_to_agent.sh /path/to/id_ed25519
# If you provide KALI_SSH_KEY_PASSPHRASE, this script will try to use `expect`
# to provide the passphrase to `ssh-add` non-interactively.

set -euo pipefail

KEY_PATH=${1:-${HOME}/.ssh/id_ed25519}
PASSPHRASE=${KALI_SSH_KEY_PASSPHRASE:-}

if [ ! -f "$KEY_PATH" ]; then
  echo "Key not found: $KEY_PATH"
  exit 2
fi

# Start ssh-agent if not running
if [ -z "${SSH_AUTH_SOCK:-}" ]; then
  eval "$(ssh-agent -s)" >/dev/null
  echo "Started ssh-agent. SSH_AUTH_SOCK=$SSH_AUTH_SOCK"
fi

if [ -n "$PASSPHRASE" ]; then
  # Non-interactive add via expect. Check if expect is installed.
  if ! command -v expect >/dev/null 2>&1; then
    echo "expect not found. Install expect (e.g. 'brew install expect' or 'sudo apt install expect') or add the key manually with 'ssh-add $KEY_PATH'"
    exit 3
  fi

  /usr/bin/expect <<EOF
log_user 1
set timeout -1
spawn ssh-add "$KEY_PATH"
expect {
  -re {Enter passphrase for .*:} {
    send -- "$PASSPHRASE\r"
    exp_continue
  }
  eof
}
EOF
else
  ssh-add "$KEY_PATH"
fi

echo "Private key added to ssh-agent. You should now be able to SSH without passphrase prompts."
