import dspy
from .base import BaseRedAgent
import os
import sys
# Ensure the `red-team` directory is on sys.path so `tools.interface` can be imported
RED_TEAM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if RED_TEAM_ROOT not in sys.path:
    sys.path.insert(0, RED_TEAM_ROOT)
from tools.interface import run_linpeas

class PrivEscSignature(dspy.Signature):
    """Analyze system enumeration to find a path to Root."""
    target_ip = dspy.InputField()
    access_level = dspy.InputField()
    vulnerabilities = dspy.InputField()
    technique = dspy.OutputField(desc="The privilege escalation technique to use, or None if none available")
    success = dspy.OutputField(desc="Whether the escalation is likely to succeed: True or False")
    reasoning = dspy.OutputField(desc="Explanation of the decision")

class PrivEscAgent(BaseRedAgent):
    def __init__(self):
        super().__init__("PRIVESC", "Escalate to Root.")
        self.decider = dspy.Predict(PrivEscSignature)

    def execute(self, target_ip):
        self.log(f"Enumerating Session {target_ip}...")
        # For now, simulate enum_data
        enum_data = "Simulated enumeration output"  # Replace with actual call
        
        # Assume access_level and vulnerabilities are from state, but since not passed, use defaults
        access_level = "LOW"
        vulnerabilities = []
        
        result = self.decider(target_ip=target_ip, access_level=access_level, vulnerabilities=str(vulnerabilities))
        self.log(f"Attempting escalation via: {result.technique}. {result.reasoning}")
        
        if result.success.lower() == "true" and result.technique:
            return {"status": "ROOT_ACQUIRED", "details": {"technique": result.technique}}
        else:
            return {"status": "FAILED", "details": {"technique": result.technique, "reasoning": result.reasoning}}