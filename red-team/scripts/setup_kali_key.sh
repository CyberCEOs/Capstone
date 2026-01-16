#!/usr/bin/env bash
# Copy a local public SSH key into the Kali container's `pentester` user
# Usage: ./setup_kali_key.sh <container-name> [path-to-public-key]

set -euo pipefail

CONTAINER=${1:-}
PUBKEY_PATH=${2:-${HOME}/.ssh/id_rsa.pub}

if [ -z "$CONTAINER" ]; then
  echo "Usage: $0 <container-name> [path-to-public-key]"
  exit 2
fi

if [ ! -f "$PUBKEY_PATH" ]; then
  echo "Public key not found at $PUBKEY_PATH"
  exit 3
fi

PUBKEY_CONTENT=$(cat "$PUBKEY_PATH")

echo "Copying public key into container '$CONTAINER' for user 'pentester'..."

docker exec -i "$CONTAINER" bash -lc "mkdir -p /home/pentester/.ssh && touch /home/pentester/.ssh/authorized_keys && chown -R pentester:pentester /home/pentester/.ssh && chmod 700 /home/pentester/.ssh && chmod 600 /home/pentester/.ssh/authorized_keys" >/dev/null

# Append the key if it's not already present
docker exec -i "$CONTAINER" bash -lc "grep -F \"$PUBKEY_CONTENT\" /home/pentester/.ssh/authorized_keys || echo \"$PUBKEY_CONTENT\" >> /home/pentester/.ssh/authorized_keys" >/dev/null

docker exec -i "$CONTAINER" bash -lc "chown pentester:pentester /home/pentester/.ssh/authorized_keys && chmod 600 /home/pentester/.ssh/authorized_keys"

echo "Public key installed. You can now SSH with your private key:" 
echo "  ssh -i ~/.ssh/id_rsa pentester@localhost -p 2222"
