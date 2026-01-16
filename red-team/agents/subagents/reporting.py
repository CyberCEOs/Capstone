from .base import BaseRedAgent
import json
from dspy import Signature
from datetime import datetime
import os

class ReportingAgent(BaseRedAgent):
    def __init__(self):
        super().__init__("REPORTING", "Compile final mission report.")

    def execute(self, campaign_data):
        self.log("Compiling Final Report...")
        
        report_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "memory", "FINAL_REPORT.md")
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

        with open(report_path, "w") as f:
            f.write(f"# Red Team Engagement Report\n")
            f.write(f"**Date:** {datetime.now()}\n\n")
            
            f.write("## 1. Executive Summary\n")
            f.write("Autonomous agents successfully breached the target perimeter...\n\n")
            
            f.write("## 2. Technical Findings\n")
            # Loop through the campaign data dictionary to print findings
            for phase, data in campaign_data.items():
                f.write(f"### {phase}\n")
                f.write(f"```json\n{json.dumps(data, indent=2)}\n```\n")
        
        self.log(f"Report saved to {report_path}")