import dspy
from .base import BaseRedAgent

class StrategySignature(dspy.Signature):
    """
    You are the Red Team Strategist (The General).
    Review the campaign state and decide the next phase based on these RULES:
    1. IF 'vulnerabilities' are found BUT 'access' is False -> You MUST choose 'ACCESS'.
    2. IF 'access' is True BUT 'is_root' is False -> You MUST choose 'PRIVESC' or 'LATERAL'.
    3. IF 'is_root' is True -> You MUST choose 'EXFIL' or 'CLEANUP'.
    4. ONLY choose 'RECON' if we have found NO vulnerabilities.
    """
    campaign_state = dspy.InputField(desc="Summary of current access, vulns, and goals")
    next_phase = dspy.OutputField(desc="Select: 'RECON', 'ACCESS', 'PRIVESC', 'LATERAL', 'EXFIL', 'CLEANUP'")
    reasoning = dspy.OutputField(desc="Explain why you are switching phases")

class StrategyAgent(BaseRedAgent):
    def __init__(self):
        super().__init__("STRATEGY", "High-level campaign planning.")
        self.decider = dspy.ChainOfThought(StrategySignature)

    def execute(self, state_summary):
        self.log(f"Analyzing Campaign State...")
        decision = self.decider(campaign_state=state_summary)
        self.log(f"Strategic Decision: {decision.next_phase} ({decision.reasoning})")
        return decision.next_phase