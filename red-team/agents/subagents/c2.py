import dspy
from .base import BaseRedAgent
from tools.interface import deploy_c2_beacon

class C2Signature(dspy.Signature):
    """
    You are the Command & Control (C2) Subagent.
    Decide the best communication channel to maintain access without triggering firewalls.
    """
    target_os = dspy.InputField(desc="Operating System of target")
    egress_rules = dspy.InputField(desc="What traffic is allowed out? (e.g., 'DNS only', 'HTTPS allowed')")
    beacon_type = dspy.OutputField(desc="Type of beacon to deploy (e.g., 'Reverse TCP', 'HTTPS', 'DNS Tunnel')")

class C2Agent(BaseRedAgent):
    def __init__(self):
        super().__init__("C2", "Maintain persistent communication channels.")
        self.decider = dspy.ChainOfThought(C2Signature)

    def deploy(self, target_ip, os_type="Linux"):
        self.log(f"Establishing C2 channel on {target_ip}...")
        
        # Ask AI for the best protocol
        plan = self.decider(target_os=os_type, egress_rules="Unknown/Assume HTTPS allowed")
        self.log(f"Selected Protocol: {plan.beacon_type}")
        
        # Execute Ryan's Tool
        result = deploy_c2_beacon(target_ip, method=plan.beacon_type)
        return result