import dspy

# --- GLOBAL CONFIGURATION ---
# This points all agents to your local BaronLLM running on Ollama.
# If you move to a different model later, you only change it here.
lm = dspy.LM('ollama_chat/baron', api_base='http://localhost:11434', api_key='')
dspy.configure(lm=lm)

class BaseRedAgent(dspy.Module):
    """
    The parent class that all Red Team agents inherit from.
    Handles logging and shared configuration.
    """
    def __init__(self, agent_name, role_description):
        super().__init__()
        self.agent_name = agent_name
        self.role = role_description
    
    def log(self, message):
        """
        Standardized logging format: [AGENT_NAME] Message
        """
        print(f"[{self.agent_name}] {message}")

    def report_error(self, error_msg):
        """
        Standardized error logging.
        """
        print(f"❌ [{self.agent_name} ERROR] {error_msg}")