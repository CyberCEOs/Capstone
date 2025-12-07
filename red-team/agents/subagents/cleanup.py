from .base import BaseRedAgent
from tools.interface import clear_event_logs

class CleanupAgent(BaseRedAgent):
    def __init__(self):
        super().__init__("CLEANUP", "Remove artifacts and logs.")

    def execute(self, session_id):
        self.log(f"Wiping logs on Session {session_id}...")
        clear_event_logs(session_id)
        self.log("Cleanup complete. Disconnecting.")