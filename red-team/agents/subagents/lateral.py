import dspy
from .base import BaseRedAgent
from tools.interface import scan_internal_network, attempt_ssh_pivot

class LateralSignature(dspy.Signature):
    """Decide where to pivot next in the internal network."""
    internal_scan = dspy.InputField()
    next_target = dspy.OutputField(desc="IP of the next high-value target")

class LateralMovementAgent(BaseRedAgent):
    def __init__(self):
        super().__init__("LATERAL", "Pivot to other machines.")
        self.decider = dspy.ChainOfThought(LateralSignature)

    def execute(self, session_id):
        self.log("Scanning internal network...")
        neighbors = scan_internal_network(session_id, "192.168.1.0/24")
        
        decision = self.decider(internal_scan=str(neighbors))
        self.log(f"Pivoting to {decision.next_target}...")
        attempt_ssh_pivot(decision.next_target)