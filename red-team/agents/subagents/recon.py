import dspy
from .base import BaseRedAgent
from tools.interface import run_nmap_scan

class ReconSignature(dspy.Signature):
    """
    You are the Reconnaissance Agent.
    Decide the scan intensity based on the mission phase.
    """
    target_ip = dspy.InputField()
    mission_phase = dspy.InputField(desc="e.g., 'Initial', 'Post-Exploit', 'Stealth'")
    scan_type = dspy.OutputField(desc="Tool command: 'nmap_fast', 'nmap_full', 'nmap_udp'")

class ReconAgent(BaseRedAgent):
    def __init__(self):
        super().__init__("RECON", "Map the attack surface.")
        self.decider = dspy.ChainOfThought(ReconSignature)

    def execute(self, target_ip, phase="Initial"):
        self.log(f"Scouting {target_ip}...")
        plan = self.decider(target_ip=target_ip, mission_phase=phase)
        
        # Execute Ryan's Nmap Tool
        results = run_nmap_scan(target_ip, scan_type=plan.scan_type)
        return results