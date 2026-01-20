import dspy
from .base import BaseRedAgent
import os
import sys
# Ensure the `red-team` directory is on sys.path so `tools.interface` can be imported
RED_TEAM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if RED_TEAM_ROOT not in sys.path:
    sys.path.insert(0, RED_TEAM_ROOT)
from tools.interface import dump_hashes

class CredAccessSignature(dspy.Signature):
    """
    You are the Credential Access Agent.
    Identify where credentials are stored (Memory, Files, DB) and dump them.
    """
    os_info = dspy.InputField()
    technique = dspy.OutputField(desc="Tool: 'Mimikatz', 'ShadowDump', 'BrowserSteal'")

class CredentialAccessAgent(BaseRedAgent):
    def __init__(self):
        super().__init__("CRED_ACCESS", "Steal user identities.")
        self.decider = dspy.ChainOfThought(CredAccessSignature)

    def execute(self, session_id):
        self.log("Hunting for credentials...")
        # Ryan needs to implement 'dump_hashes'
        creds = dump_hashes(session_id)
        self.log(f"Dumped {len(creds)} hashes.")
        return creds