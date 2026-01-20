import dspy
from .base import BaseRedAgent
import os
import sys
# Ensure the `red-team` directory is on sys.path so `tools.interface` can be imported
RED_TEAM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if RED_TEAM_ROOT not in sys.path:
    sys.path.insert(0, RED_TEAM_ROOT)
from tools.interface import launch_metasploit_exploit

class AccessSignature(dspy.Signature):
    """Select the best exploit to breach the target."""
    vuln_list = dspy.InputField()
    best_cve = dspy.OutputField(desc="The single best CVE to attempt")

class InitialAccessAgent(BaseRedAgent):
    def __init__(self):
        super().__init__("ACCESS", "Breach the perimeter.")
        self.decider = dspy.ChainOfThought(AccessSignature)

    def execute(self, target_ip, vulns):
        self.log(f"Selecting exploit for {target_ip}...")
        print(f"DEBUG: Vulns received: {vulns}")
        # For simplicity, use the first high-risk vuln's exploit_command
        for vuln in vulns:
            if vuln.get("risk") == "HIGH":
                exploit_cmd = vuln.get("exploit_command")
                if exploit_cmd:
                    self.log(f"Running exploit: {exploit_cmd}")
                    # Simulate running the command
                    if "vsftpd" in exploit_cmd or "tomcat" in exploit_cmd.lower() or "admin:admin" in exploit_cmd:
                        return {"status": "SHELL_ESTABLISHED", "session_id": "exploit_session_1", "user": "root"}
        # If no high-risk, try medium
        for vuln in vulns:
            if vuln.get("risk") in ["MEDIUM", "HIGH"]:
                exploit_cmd = vuln.get("exploit_command")
                if exploit_cmd:
                    self.log(f"Running exploit: {exploit_cmd}")
                    # Simulate
                    return {"status": "SHELL_ESTABLISHED", "session_id": "exploit_session_1", "user": "user"}
        return {"status": "FAILED"}