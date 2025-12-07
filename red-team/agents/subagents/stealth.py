import dspy
from .base import BaseRedAgent
from tools.interface import clear_event_logs

class StealthSignature(dspy.Signature):
    """
    You are the Stealth & Evasion Subagent.
    Analyze the current alert level and recommend evasion techniques.
    """
    blue_team_status = dspy.InputField(desc="Current alert level (e.g., 'High', 'Low', 'Unknown')")
    planned_action = dspy.InputField(desc="The action we want to take (e.g., 'Nmap Scan')")
    modification = dspy.OutputField(desc="How to modify the action (e.g., 'Use -T2 timing', 'Fragment packets')")
    reasoning = dspy.OutputField(desc="Why this lowers detection probability")

class StealthAgent(BaseRedAgent):
    def __init__(self):
        super().__init__("STEALTH", "Minimize noise and avoid detection.")
        self.decider = dspy.ChainOfThought(StealthSignature)

    def advise(self, action, blue_status="Unknown"):
        self.log(f"Analyzing OPSEC for action: {action}")
        advice = self.decider(blue_team_status=blue_status, planned_action=action)
        self.log(f"Advisory: {advice.modification}")
        return advice.modification

    def wipe_tracks(self, session_id):
        self.log(f"Initiating Log Wipe on Session {session_id}...")
        # Call Ryan's tool to clear Bash history / Windows Event Logs
        success = clear_event_logs(session_id)
        return success