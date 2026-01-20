from .base import BaseRedAgent
import os
import sys
# Ensure the `red-team` directory is on sys.path so `tools.interface` can be imported
RED_TEAM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if RED_TEAM_ROOT not in sys.path:
    sys.path.insert(0, RED_TEAM_ROOT)
from tools.interface import clear_event_logs

class CleanupAgent(BaseRedAgent):
    def __init__(self):
        super().__init__("CLEANUP", "Remove artifacts and logs.")

    def execute(self, session_id):
        self.log(f"Wiping logs on Session {session_id}...")
        clear_event_logs(session_id)
        self.log("Cleanup complete. Disconnecting.")