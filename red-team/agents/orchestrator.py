import dspy
import json
import os
import sys
import time # Added for potential logging delay or timeout
from datetime import datetime, timezone

# --- START PATH FIX (Required to find 'subagents' and 'tools') ---
# This tells Python to look in the current directory ('agents') for modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# --- END PATH FIX ---

# Standard imports (will now work)
from subagents.strategy import StrategyAgent
from subagents.recon import ReconAgent
# Map to actual subagent modules/classes present in repo
from subagents.initial_access import InitialAccessAgent
from subagents.privesc import PrivEscAgent
from subagents.exfiltration import ExfiltrationAgent
from subagents.reporting import ReportingAgent

# Configuration
TARGET_IP = os.environ.get("TARGET_IP", "10.0.0.10") # Default or environment var

# --- Orchestrator Class ---

class Orchestrator:
    def __init__(self, target_ip):
        self.target_ip = target_ip
        self.state = {
            "initial_target": target_ip,
            "current_target": target_ip,
            "vulnerabilities": [],
            "access": False,
            "is_root": False,
            "exfiltrated": False,
            "lateral_attempts": 0, # NEW: Counter for loop detection
            "recon_attempts": 0,
            "exfil_attempts": 0,  # NEW: Counter for EXFIL loop detection
            "privesc_attempts": 0,  # NEW: Counter for PRIVESC loop detection
            "campaign_log_path": os.path.join(
                os.path.dirname(os.path.dirname(__file__)), # Go up to red-team/
                "memory", 
                "logs", 
                "campaign_log.json"
            )
        }
        
        # Initialize Subagents. When `AUTO_RUN` is enabled we avoid instantiating
        # LLM-backed subagents (they can perform network calls during construction).
        if os.environ.get("AUTO_RUN"):
            self.strategy = None
            self.recon = None
            self.access = None
            self.privexec = None
            self.exfil = None
            # Reporting writes a file and does not require LLM initialization
            self.reporting = ReportingAgent()
        else:
            self.strategy = StrategyAgent()
            self.recon = ReconAgent()
            self.access = InitialAccessAgent()
            self.privexec = PrivEscAgent()
            self.exfil = ExfiltrationAgent()
            self.reporting = ReportingAgent()
        
        self._setup_logging()

    def _setup_logging(self):
        # Ensure log directory exists
        log_dir = os.path.dirname(self.state['campaign_log_path'])
        os.makedirs(log_dir, exist_ok=True)
        # Clear previous logs for a fresh run
        if os.path.exists(self.state['campaign_log_path']):
            os.remove(self.state['campaign_log_path'])

    def _log_action(self, phase, status, details=None):
        action_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": phase,
            "status": status,
            "target": self.state['current_target'],
            "details": details or {}
        }
        with open(self.state['campaign_log_path'], 'a') as f:
            f.write(json.dumps(action_data) + '\n')

    def run_campaign(self):
        print(f"🚀 Starting Orchestrator Campaign against {self.target_ip}...")
        phase = "RECON"
        max_steps = int(os.environ.get("ORCHESTRATOR_MAX_STEPS", "40"))
        step_count = 0

        # If AUTO_RUN is set, skip LLM-driven strategy and execute a deterministic
        # sequence of phases to allow simulated exploitation without calling the LLM.
        if os.environ.get("AUTO_RUN"):
            print("[ORCHESTRATOR] AUTO_RUN enabled — executing deterministic phase sequence.")
            # RECON (simulated — bypass LLM)
            nmap_raw = {"ip": self.state['current_target'], "open_ports": [{"port": 22, "service": "ssh"}, {"port": 3000, "service": "http-alt"}]}
            output = {
                "phase": "RECON",
                "target": self.state['current_target'],
                "nmap_raw": nmap_raw,
                "vulnerabilities": [
                    {"summary": "Simulated: weak credentials", "risk": "HIGH", "exploit_command": f"ssh user@{self.state['current_target']}"}
                ],
                "reasoning": "AUTO_RUN: simulated reconnaissance results"
            }
            self.state['vulnerabilities'].extend(output.get('vulnerabilities', []))
            self._log_action("RECON", "COMPLETE", output)

            # ACCESS (simulated)
            access_output = {"status": "SHELL_ESTABLISHED", "session_id": "session_sim_1"}
            if access_output.get("status") == "SHELL_ESTABLISHED":
                self.state['access'] = True
            self._log_action("ACCESS", access_output.get("status", "FAILED"), access_output)

            # PRIVESC (simulated)
            privesc_output = {"status": "ROOT_ACQUIRED", "details": {"technique": "SUDO_NOPASSWD"}}
            if privesc_output.get("status") == "ROOT_ACQUIRED":
                self.state['is_root'] = True
            self._log_action("PRIVESC", privesc_output.get("status", "FAILED"), privesc_output)

            # EXFIL (simulated)
            exfil_output = {"status": "DATA_EXFILTRATED", "file": "/etc/passwd"}
            if exfil_output.get("status") == "DATA_EXFILTRATED":
                self.state['exfiltrated'] = True
            self._log_action("EXFIL", exfil_output.get("status", "FAILED"), exfil_output)

            # REPORT
            print("\n--- FINAL PHASE: REPORT (AUTO_RUN) ---")
            self.reporting.execute(self.state)
            print("🏁 AUTO_RUN complete. Campaign log saved.")
            return

        while phase != "REPORT":
            # Global step counter to prevent infinite loops
            step_count += 1
            if step_count > max_steps:
                print(f"\n[OVERRIDE] Maximum orchestrator steps exceeded ({max_steps}). Forcing REPORT.")
                phase = "REPORT"
                break
            self._log_action("START_PHASE", "ACTIVE", {"phase": phase})
            print(f"\n--- EXECUTION PHASE: {phase} ---")
            
            # --- PHASE EXECUTION ---
            if phase == "RECON":
                # Implementation of ReconAgent
                output = self.recon.execute(self.state['current_target'])
                self.state['vulnerabilities'].extend(output['vulnerabilities'])
                self._log_action(phase, "COMPLETE", output)
                
            elif phase == "ACCESS":
                # Implementation of InitialAccessAgent
                # `InitialAccessAgent.execute` expects (target_ip, vulns)
                output = self.access.execute(self.state['current_target'], self.state['vulnerabilities'])
                if output.get("status") == "SHELL_ESTABLISHED":
                    self.state['access'] = True
                self._log_action(phase, output.get("status", "FAILED"), output)

            elif phase == "PRIVESC":
                # Implementation of PrivEscAgent
                output = self.privexec.execute(self.state['current_target'])
                if output.get("status") == "ROOT_ACQUIRED" and output.get("details", {}).get("technique"):
                    self.state['is_root'] = True
                self._log_action(phase, output.get("status", "FAILED"), output)

            elif phase == "LATERAL":
                # Implementation of Lateral Movement (SIMULATED)
                print("[*] (SIMULATION) Pivoting to 192.168.1.50...")
                self._log_action(phase, "SIMULATED", {"target_ip": "192.168.1.50"})
                # Give it a moment to avoid immediate loop repetition
                time.sleep(1) 
            
            elif phase == "EXFIL":
                # Implementation of ExfilAgent
                output = self.exfil.execute(self.state['current_target'])
                if output.get("status") == "DATA_EXFILTRATED":
                    self.state['exfiltrated'] = True
                self._log_action(phase, output.get("status", "FAILED"), output)

            else:
                print(f"[ERROR] Unknown phase: {phase}. Defaulting to REPORT.")
                phase = "REPORT"
                break
            
            # --- HRL STRATEGY: Determine Next Phase ---
            summary = self._create_state_summary()
            print("[STRATEGY] Analyzing Campaign State...")
            
            # NEW: Update lateral attempt counter and reset for other phases
            if phase == "LATERAL":
                self.state['lateral_attempts'] += 1
            else:
                self.state['lateral_attempts'] = 0 

            if phase == "RECON":
                self.state['recon_attempts'] += 1
            else:
                self.state['recon_attempts'] = 0 

            if phase == "EXFIL":
                self.state['exfil_attempts'] += 1
            else:
                self.state['exfil_attempts'] = 0

            if phase == "PRIVESC":
                self.state['privesc_attempts'] += 1
            else:
                self.state['privesc_attempts'] = 0 

            # --- LOGIC OVERRIDE (ANTI-OSCILLATION) ---
            next_phase = "DECISION"

            # A. Override: Detect if stuck in LATERAL loop (> 3 attempts)
            if self.state['lateral_attempts'] > 3:
                print("\n[OVERRIDE] 🚨 LATERAL MOVEMENT STUCK. Forcing final action.")
                next_phase = "REPORT"
            # B. Override: Detect if stuck in RECON loop (> 2 attempts)
            elif self.state['recon_attempts'] > 2:
                print("\n[OVERRIDE] 🚨 RECON LOOP DETECTED. Forcing ACCESS phase.")
                next_phase = "ACCESS"
            # C. Override: Detect if stuck in EXFIL loop (> 3 attempts)
            elif self.state['exfil_attempts'] > 3:
                print("\n[OVERRIDE] 🚨 EXFIL LOOP DETECTED. Forcing REPORT.")
                next_phase = "REPORT"
            # D. Override: Detect if stuck in PRIVESC loop (> 3 attempts)
            elif self.state['privesc_attempts'] > 3:
                print("\n[OVERRIDE] 🚨 PRIVESC LOOP DETECTED. Forcing EXFIL.")
                next_phase = "EXFIL"
            # E. Override: Force EXFIL after Root Access
            elif self.state.get("is_root") and not self.state.get("exfiltrated"):
                print("[OVERRIDE] Root access achieved. Forcing EXFIL phase.")
                next_phase = "EXFIL"
            
            # F. Override: Force REPORT after Exfiltration
            elif self.state.get("exfiltrated"):
                print("[OVERRIDE] Exfil complete. Forcing REPORT phase.")
                next_phase = "REPORT"
            
            else:
                # Fallback to AI decision if state is ambiguous
                next_phase = self.strategy.execute(summary)
                # Map EXPLOIT to ACCESS
                if next_phase == "EXPLOIT":
                    next_phase = "ACCESS"
            
            # Set the new phase
            # Detect simple oscillation: if the last two phases are identical repeatedly,
            # increment lateral_attempts as a heuristic and break if needed.
            phase = next_phase

        print("\n--- FINAL PHASE: REPORT ---")
        self.reporting.execute(self.state)
        print("🏁 Mission Complete. Campaign log saved.")

    def _create_state_summary(self):
        # Simple string summary for the Strategy Agent
        summary = f"""
Current Target: {self.state['current_target']}
Access Status: {'SHELL ESTABLISHED' if self.state['access'] else 'NONE'}
Privilege Status: {'ROOT ACCESS' if self.state['is_root'] else 'LOW'}
Data Exfiltration: {'COMPLETE' if self.state['exfiltrated'] else 'PENDING'}
Vulnerabilities Found: {len(self.state['vulnerabilities'])}
"""
        return summary.strip()

# --- Execution ---
if __name__ == "__main__":
    # Use the centralized LLM configuration in `subagents/base.py`.
    # To force a local/alternative configuration here set `FORCE_LLM_CONFIG=1`.
    if os.environ.get("FORCE_LLM_CONFIG"):
        print("🧠 FORCE_LLM_CONFIG set — initializing local LLM override...")
        # Example override (only used when FORCE_LLM_CONFIG is set)
        dspy.configure(
            lm=dspy.OllamaLocal(model='llama3.1', max_tokens=2048, timeout=30),
            trace=[]
        )
    else:
        print("🧠 Using centralized LLM configuration (subagents/base.py)")

    # Run the campaign
    campaign = Orchestrator(TARGET_IP)
    campaign.run_campaign()