import os
import sys
import json

# Make import robust: add the `agents` dir to sys.path so this script can be
# run from the repository root or any working directory.
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
AGENTS_DIR = os.path.normpath(os.path.join(THIS_DIR, ".."))
if AGENTS_DIR not in sys.path:
    sys.path.insert(0, AGENTS_DIR)

# Import the centralized base module which configures dspy
try:
    from subagents import base
except Exception as e:
    print(f"Failed to import subagents.base: {e}")
    base = None

print("--- LLM Configuration Check ---")
if base:
    print(f"DEFAULT_LLM / CLAUDE_MODEL: {getattr(base, 'CLAUDE_MODEL', '<not set>')}")
    print(f"HUGGINGFACE_MODEL: {getattr(base, 'HUGGINGFACE_MODEL', '<not set>')}")
    print(f"LLM_API_BASE: {getattr(base, 'LLM_API_BASE', '<not set>')}")
    print(f"LLM_API_KEY set: {'yes' if getattr(base, 'LLM_API_KEY', '') else 'no'}")
    try:
        lm = getattr(base, 'lm', None)
        print(f"Configured LM object: {repr(lm)}")
    except Exception as e:
        print(f"Error reading configured lm object: {e}")
else:
    print("Base module not available; check your PYTHONPATH and package imports.")

print("\nTo use your Hugging Face BaronLLM (GGUF) locally, set:")
print("  export HUGGINGFACE_MODEL=\"AlicanKiraz0/Cybersecurity-BaronLLM_Offensive_Security_LLM_Q6_K_GGUF\"")
print("  export DEFAULT_LLM=\"huggingface:$HUGGINGFACE_MODEL\"")
print("Then run from repo root: python3 red-team/agents/tools/check_llm.py\n")
print("Or run from inside agents/: cd red-team/agents && python3 tools/check_llm.py")
