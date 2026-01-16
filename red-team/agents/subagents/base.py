import dspy
import os

# --- GLOBAL CONFIGURATION ---
# Centralize LLM selection for all agents here. Use one of the env vars:
# - `DEFAULT_LLM` (preferred): the provider-specific model identifier.
# - `HUGGINGFACE_MODEL`: a shorthand for your Hugging Face model.
# Examples:
#   export HUGGINGFACE_MODEL="AlicanKiraz0/Cybersecurity-BaronLLM_Offensive_Security_LLM_Q6_K_GGUF"
#   export DEFAULT_LLM="huggingface:AlicanKiraz0/Cybersecurity-BaronLLM_Offensive_Security_LLM_Q6_K_GGUF"
# If you run a local Ollama service, you can use `ollama_chat/baron` or set
# `FORCE_LLM_CONFIG=1` in `orchestrator.py` to override with an OllamaLocal instance.

# Prefer user-provided env vars. If none are provided, default to the
# Hugging Face BaronLLM you mentioned (GGUF) via the `huggingface:` prefix.
HUGGINGFACE_MODEL = os.environ.get("HUGGINGFACE_MODEL")
CLAUDE_MODEL = (
    os.environ.get("DEFAULT_LLM")
    or os.environ.get("CLAUDE_MODEL")
    or (f"huggingface:{HUGGINGFACE_MODEL}" if HUGGINGFACE_MODEL else None)
    or "huggingface:AlicanKiraz0/Cybersecurity-BaronLLM_Offensive_Security_LLM_Q6_K_GGUF"
)

# Optional connection details (used by some dspy backends)
LLM_API_BASE = os.environ.get("LLM_API_BASE", "")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")

# Create the LM using dspy generic constructor. The exact semantics of the
# model string (prefixes like `huggingface:` or `ollama_chat/`) are passed
# through to the underlying dspy implementation which your environment
# (Ollama/huggingface CLI/other) should support.
# If you are using Ollama locally, you can set `OLLAMA_MODEL_NAME` to the
# Ollama model id (for example `baron`). When present we prefer an
# OllamaLocal instance which uses the local Ollama daemon.
OLLAMA_MODEL_NAME = os.environ.get("OLLAMA_MODEL_NAME")
OLLAMA_API_BASE = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434")
OLLAMA_TIMEOUT_S = int(os.environ.get("OLLAMA_TIMEOUT_S", "60"))

# Optional MCP (Model Context Protocol) support. Set USE_MCP=1 and provide
# MCP_API_BASE to route LM requests through an MCP-compatible proxy/server
# such as a Hextstrike MCP instance.
USE_MCP = os.environ.get("USE_MCP", "0") == "1"
MCP_API_BASE = os.environ.get("MCP_API_BASE", os.environ.get("OLLAMA_API_BASE", ""))
MCP_API_KEY = os.environ.get("MCP_API_KEY", "")

if OLLAMA_MODEL_NAME:
    try:
        # Set a reasonable request timeout to avoid long hangs when Ollama is unresponsive
        lm = dspy.OllamaLocal(model=OLLAMA_MODEL_NAME, base_url=OLLAMA_API_BASE, timeout_s=OLLAMA_TIMEOUT_S)
        # Quick health log
        print(f"[LLM] Using Ollama model '{OLLAMA_MODEL_NAME}' at {OLLAMA_API_BASE} (timeout={OLLAMA_TIMEOUT_S}s)")
        dspy.configure(lm=lm)
    except Exception:
        # Fall back to generic constructor if OllamaLocal isn't available
        lm = dspy.LM(CLAUDE_MODEL, api_base=LLM_API_BASE, api_key=LLM_API_KEY)
        dspy.configure(lm=lm)
else:
    # If USE_MCP is set, prefer routing LM traffic through the MCP proxy
    if USE_MCP and MCP_API_BASE:
        try:
            print(f"[LLM] Using MCP proxy at {MCP_API_BASE} for model {CLAUDE_MODEL}")
            lm = dspy.LM(CLAUDE_MODEL, api_base=MCP_API_BASE, api_key=MCP_API_KEY)
            dspy.configure(lm=lm)
        except Exception as e:
            print(f"[LLM] Failed to configure MCP proxy client: {e}. Falling back to default LM.")
            lm = dspy.LM(CLAUDE_MODEL, api_base=LLM_API_BASE, api_key=LLM_API_KEY)
            dspy.configure(lm=lm)
    else:
        lm = dspy.LM(CLAUDE_MODEL, api_base=LLM_API_BASE, api_key=LLM_API_KEY)
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