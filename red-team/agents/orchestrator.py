import sys
import os
import dspy

# 1. Path Hacking: Ensure we can import from subfolders
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- IMPORT THE FULL ARMY ---
from subagents.strategy import StrategyAgent
from subagents.recon import ReconAgent
from subagents.vuln_analyst import VulnAnalystAgent
from subagents.initial_access import InitialAccessAgent
from subagents.web_exploit import WebExploitAgent
from subagents.c2 import C2Agent
from subagents.internal_discovery import InternalDiscoveryAgent
from subagents.cred_access import CredentialAccessAgent
from subagents.privesc import PrivEscAgent
from subagents.lateral import LateralMovementAgent
from subagents.persistence import PersistenceAgent
from subagents.collection import CollectionAgent
from subagents.exfiltration import ExfiltrationAgent
from subagents.impact import ImpactAgent
from subagents.stealth import StealthAgent
from subagents.documentation import DocumentationAgent
from subagents.cleanup import CleanupAgent
from subagents.reporting import ReportingAgent

class RedTeamOrchestrator:
    def __init__(self, target_ip):
        self.target_ip = target_ip
        
        # --- INITIALIZE THE SQUAD ---
        self.strategy = StrategyAgent()
        self.docs = DocumentationAgent()
        self.reporter = ReportingAgent()
        self.stealth = StealthAgent()

        self.recon = ReconAgent()
        self.vuln = VulnAnalystAgent()
        self.web = WebExploitAgent()
        self.access = InitialAccessAgent()
        self.c2 = C2Agent()
        self.discovery = InternalDiscoveryAgent()
        self.creds = CredentialAccessAgent()
        self.privesc = PrivEscAgent()
        self.lateral = LateralMovementAgent()
        self.persistence = PersistenceAgent()
        self.collection = CollectionAgent()
        self.exfil = ExfiltrationAgent()
        self.impact = ImpactAgent()
        self.cleanup = CleanupAgent()

        # --- CAMPAIGN STATE ---
        self.state = {
            "phase": "START",
            "access": False, 
            "is_root": False, 
            "session_id": None,
            "vulns": [],
            "creds_found": []
        }

    def run_campaign(self):
        print(f"💀 [OVERLORD] Initializing Kill Chain against {self.target_ip}...")
        self.docs.record_engagement("START", "INIT", {"target": self.target_ip})

        while True:
            # --- CREATE A CLEAN SUMMARY FOR THE AI ---
            vuln_count = len(self.state["vulns"])
            summary = (
                f"Current Target: {self.target_ip}. "
                f"Access Established: {self.state['access']}. "
                f"Root Access: {self.state['is_root']}. "
                f"Vulnerabilities Found: {vuln_count}. "
                f"Session ID: {self.state['session_id']}."
            )
            
            # Ask the General (Strategy Agent)
            next_phase = self.strategy.execute(summary)
            
            # --- PHASE 1: DISCOVERY ---
            if "RECON" in next_phase.upper():
                scan_data = self.recon.execute(self.target_ip)
                self.state["scan_data"] = scan_data
                vulns = self.vuln.execute(scan_data)
                self.state["vulns"] = vulns

            # --- PHASE 2: ACCESS ---
            elif "ACCESS" in next_phase.upper():
                if not self.state["vulns"]:
                    print("❌ No vulnerabilities. General ordered Access but we have no targets.")
                    continue 
                    
                result = self.access.execute(self.target_ip, self.state["vulns"])
                if result.get("success"):
                    self.state["access"] = True
                    self.state["session_id"] = result["session_id"]
                    print("✅ Shell Established!")
                    
                    # Deploy C2/Persistence immediately
                    self.c2.deploy(self.target_ip)
                    self.persistence.execute(os_type="Linux")
                else:
                    print("❌ Access Failed.")
                    break

            # --- PHASE 3: POST-EXPLOIT ---
            elif "PRIVESC" in next_phase.upper():
                if not self.state["access"]: continue
                result = self.privesc.execute(self.state["session_id"])
                if result.get("success"):
                    self.state["is_root"] = True

            elif "LATERAL" in next_phase.upper():
                if not self.state["access"]: continue
                self.lateral.execute(self.state["session_id"])

            elif "EXFIL" in next_phase.upper():
                self.exfil.execute(self.state["session_id"])

            # --- CLEANUP ---
            elif "CLEANUP" in next_phase.upper():
                if self.state["session_id"]:
                    self.cleanup.execute(self.state["session_id"])
                self.reporter.execute(self.state)
                print("🏁 Mission Complete.")
                break
            else:
                print(f"⚠️ Unknown Phase: {next_phase}")
                break

# --- EXECUTION BLOCK (MUST BE UNINDENTED) ---
if __name__ == "__main__":
    print("🚀 Starting Orchestrator...")
    
    # Use 127.0.0.1 for Simulation
    TARGET = "127.0.0.1" 
    
    campaign = RedTeamOrchestrator(TARGET)
    campaign.run_campaign()