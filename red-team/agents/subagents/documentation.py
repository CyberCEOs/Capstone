import json
import os
from datetime import datetime
from .base import BaseRedAgent

LOG_DIR = "../memory/logs"  # Relative path to red-team/memory/logs

class DocumentationAgent(BaseRedAgent):
    def __init__(self):
        super().__init__("DOCS", "Record all operations for the Dashboard.")
        os.makedirs(LOG_DIR, exist_ok=True)

    def record_engagement(self, phase, status, details):
        """
        Saves a structured log entry for the Dashboard to consume.
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": "RedTeam",
            "phase": phase,          # e.g., "PHASE_1_RECON"
            "status": status,        # e.g., "SUCCESS", "DETECTED"
            "details": details       # Dictionary of specific data
        }
        
        # Save to a running log file
        log_file = f"{LOG_DIR}/campaign_log.json"
        
        # Append mode (creates a JSON lines format)
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
            
        self.log(f"Recorded event: {phase} -> {status}")