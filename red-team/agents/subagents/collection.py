import dspy
from .base import BaseRedAgent
import os
import sys
# Ensure the `red-team` directory is on sys.path so `tools.interface` can be imported
RED_TEAM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if RED_TEAM_ROOT not in sys.path:
    sys.path.insert(0, RED_TEAM_ROOT)
from tools.interface import search_sensitive_files

class CollectionSignature(dspy.Signature):
    """
    You are the Collection Agent.
    Decide what files are high-value targets based on the system type.
    """
    system_role = dspy.InputField(desc="e.g., 'Database Server', 'HR Laptop'")
    keywords = dspy.OutputField(desc="Search terms: 'salary', 'password', 'api_key'")

class CollectionAgent(BaseRedAgent):
    def __init__(self):
        super().__init__("COLLECTION", "Locate sensitive data.")
        self.decider = dspy.ChainOfThought(CollectionSignature)

    def execute(self, session_id, role="General Server"):
        self.log(f"Targeting files for role: {role}...")
        plan = self.decider(system_role=role)
        
        # Simple string split for the demo
        kw_list = plan.keywords.replace(" ", "").split(",")
        return search_sensitive_files(session_id, kw_list)