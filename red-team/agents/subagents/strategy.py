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
        # Last-ditch: try top-level exports (older/newer packaging variations)
        try:
            from dspy import InputField, OutputField
        except Exception:
            raise ImportError("Could not import InputField/OutputField from dspy; check your dspy version.")

# Define the Signature for the Strategy Agent's task
class StrategySignature(Signature):
    """Given the current campaign state, decide the next strategic phase of engagement."""
    # Use InputField/OutputField for signature fields
    campaign_state = InputField(desc="A summarized string of the campaign's current access and privilege status.")
    strategy_choice = OutputField(desc="The next phase to execute. Must be one of: RECON, ACCESS, PRIVESC, LATERAL, EXFIL, or REPORT.")
    reasoning = OutputField(desc="Detailed reasoning for the chosen strategy based on the current state.")

# ... (rest of the file remains the same)
# Strategy Agent
class StrategyAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        # Use ChainOfThought for robust decision making
        self.decider = dspy.ChainOfThought(StrategySignature)

    def execute(self, state_summary: str) -> str:
        # Use the Decider module to get a strategic choice
        decision = self.decider(campaign_state=state_summary)

        # Print raw decision for debugging and be resilient to different DSPy return shapes
        try:
            print(f"[STRATEGY] Raw decision: {decision}")
        except Exception:
            print("[STRATEGY] Raw decision (repr):", repr(decision))

        # Try common attribute names used across dsp versions
        choice = None
        for attr in ("strategy_choice", "choice", "strategy", "decision", "best_choice"):
            choice = getattr(decision, attr, None)
            if choice:
                break

        # If the model returned nothing useful, apply a safe fallback to progress the campaign
        if not choice:
            print("[STRATEGY] Empty or invalid model decision — falling back to 'ACCESS'")
            return "ACCESS"

        print(f"[STRATEGY] Strategic Decision: {choice}")
        return choice