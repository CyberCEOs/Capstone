# test_c2.py
import sys
sys.path.append('..')  # Add parent directory to path for tools import

from subagents.c2 import C2Agent

print("Starting C2 agent test...")

agent = C2Agent()
result = agent.deploy(
    target_ip="192.168.56.101",
    os_type="Linux",
    egress_rules="HTTPS allowed"
)

print("Deployment result:", result)