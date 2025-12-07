import dspy
from .base import BaseRedAgent
# Ryan needs to add 'run_whoami', 'run_ip_route' to interface
from tools.interface import scan_internal_network

class DiscoverySignature(dspy.Signature):
    """
    You are the Internal Discovery Agent.
    Once inside, figure out where we are and what neighbors exist.
    """
    current_shell_output = dspy.InputField(desc="Output of 'ip a' or 'whoami'")
    next_action = dspy.OutputField(desc="Command to run: 'ARP_Scan', 'Ping_Sweep', 'User_Enum'")

class InternalDiscoveryAgent(BaseRedAgent):
    def __init__(self):
        super().__init__("DISCOVERY", "Map the internal network.")
        self.decider = dspy.ChainOfThought(DiscoverySignature)

    def execute(self, session_id):
        self.log(f"Surveying internal environment (Session {session_id})...")
        
        # Simulating shell output for the AI decision
        dummy_shell = "inet 192.168.1.5/24 brd 192.168.1.255"
        
        plan = self.decider(current_shell_output=dummy_shell)
        self.log(f"Running: {plan.next_action}")
        
        return scan_internal_network(session_id, "192.168.1.0/24")