## Kali Docker for Capstone agents

This document explains how to build and run a Kali container that your agents can use
as an attacker host. The container exposes SSH and includes `nmap`, `sshpass`, and `linpeas`.

Files added:
- `docker/kali/Dockerfile` — builds a Kali-based image with SSH and basic tools
- `docker-compose.yml` — builds and runs the Kali container and mounts `./red-team` into `/home/pentester/workspace`

Build and run
1. From the repository root, build and start the Kali container:

```bash
docker compose up --build -d kali
```

2. Verify the container is running and SSH is reachable at host port `2222`:

```bash
# on host
ssh pentester@localhost -p 2222
# password: kali
```

Connecting the agents
- Option A: Run orchestrator on your host and have it call Kali via SSH (recommended):

Set environment variables for live mode and Kali host:

```bash
export LIVE_MODE=1
export KALI_SSH_HOST=localhost
export KALI_SSH_PORT=2222
export KALI_SSH_USER=pentester
export KALI_SSH_PASS=kali
export TARGET_IP=192.168.4.50
# optionally set TARGET_SSH_USER/TARGET_SSH_PASS for the target VM
export TARGET_SSH_USER=root
export TARGET_SSH_PASS=toor

# Run orchestrator
python3 red-team/agents/orchestrator.py
```

- Option B: Run the orchestrator inside the Kali container (agents run from Kali):

```bash
docker exec -it capstone_kali bash
# inside container
cd workspace
# create or activate a Python venv and install requirements, then run:
python3 agents/orchestrator.py
```

Notes and safety
- You confirmed this is your lab VM; keep `LIVE_MODE` off on production networks.
- Metasploit is **not** installed by default in the provided Dockerfile (it's large). If you need it, install `metasploit-framework` inside the Kali container.
- LinPEAS is preinstalled in `/opt/linpeas/linpeas.sh` inside the container.

If you want, I can:
- Add a small `run_kali.sh` helper script to build/start the container and export example env vars.
- Add Metasploit installation to the Dockerfile (note: large image size and long build time).
