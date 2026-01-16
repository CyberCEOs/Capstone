import dspy
from dspy import Signature

# Support multiple dspy versions: prefer `InputField`/`OutputField`, fallback to
# `OldInputField`/`OldOutputField` if present.
try:
    from dspy.primitives import InputField, OutputField
except Exception:
    try:
        from dspy.primitives import OldInputField as InputField, OldOutputField as OutputField
    except Exception:
        try:
            from dspy import InputField, OutputField
        except Exception:
            raise ImportError("Could not import InputField/OutputField from dspy; check dspy version.")

import os
import sys
# Ensure the `red-team` directory is on sys.path so `tools.interface` can be imported
# when the script is run directly (e.g. `python3 red-team/agents/orchestrator.py`).
RED_TEAM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if RED_TEAM_ROOT not in sys.path:
    sys.path.insert(0, RED_TEAM_ROOT)
from tools.interface import run_nmap_scan
import json

# Define the Signature for the Recon Agent's task
class ReconSignature(Signature):
    """Analyze the Nmap scan output and identify the single most critical vulnerability (CVE or misconfiguration)."""
    # nmap_output is provided as input to the Signature; the rest are outputs
    nmap_output = InputField(desc="The output from the Nmap scan.")
    vulnerability = OutputField(desc="The most critical vulnerability found (e.g., CVE-2021-1234 or 'anonymous ftp access').")
    risk_level = OutputField(desc="The calculated risk level: HIGH, MEDIUM, or LOW.")
    exploit_command = OutputField(desc="A proposed exploit command or next step for the Access phase.")

# Reconnaissance Agent
class ReconAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.scanner = dspy.ChainOfThought(ReconSignature)

    def execute(self, target_ip):
        # 1. Run the external tool (Nmap)
        print(f"[{self.__class__.__name__}] Running Nmap scan against {target_ip}...")
        nmap_output = run_nmap_scan(target_ip) # This calls the interface tool
        
        # 2. Process output using LLM (Strategy)
        print(f"[{self.__class__.__name__}] Analyzing output with LLM...")
        # ChainOfThought/signature expects string inputs for formatting; serialize the
        # nmap output dict into JSON so DSPy templates can format it correctly.
        analysis = self.scanner(nmap_output=json.dumps(nmap_output))

        # 3. Format the result
        # DSPy prediction objects can expose different attributes across versions;
        # be resilient when extracting fields.
        vuln_summary = getattr(analysis, 'vulnerability', None) or getattr(analysis, 'summary', None) or None
        risk = getattr(analysis, 'risk_level', None) or getattr(analysis, 'risk', None) or None
        exploit_cmd = getattr(analysis, 'exploit_command', None) or getattr(analysis, 'exploit', None) or None
        reasoning = (
            getattr(analysis, 'thought', None)
            or getattr(analysis, 'reasoning', None)
            or getattr(analysis, 'explanation', None)
            or getattr(analysis, 'chain_of_thought', None)
            or str(analysis)
        )

        result = {
            "phase": "RECON",
            "target": target_ip,
            "nmap_raw": nmap_output,
            "vulnerabilities": [
                {
                    "summary": vuln_summary,
                    "risk": risk,
                    "exploit_command": exploit_cmd
                }
            ],
            "reasoning": reasoning
        }
        
        return result