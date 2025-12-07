import dspy
from .base import BaseRedAgent
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
        decision = self.decider(vuln_list=str(vulns))
        
        # Trigger Ryan's Metasploit Wrapper
        result = launch_metasploit_exploit(target_ip, decision.best_cve)
        return result