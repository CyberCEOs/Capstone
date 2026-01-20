import dspy
import os

# --- GLOBAL CONFIGURATION ---
# Prefer env vars for flexibility
HUGGINGFACE_MODEL = os.environ.get("HUGGINGFACE_MODEL")
DEFAULT_LLM = (
    os.environ.get("DEFAULT_LLM")
    or os.environ.get("CLAUDE_MODEL")
    or (f"huggingface:{HUGGINGFACE_MODEL}" if HUGGINGFACE_MODEL else None)
    or "huggingface:AlicanKiraz0/Cybersecurity-BaronLLM_Offensive_Security_LLM_Q6_K_GGUF"
)

OLLAMA_MODEL_NAME = os.environ.get("OLLAMA_MODEL_NAME") or "hf.co/AlicanKiraz0/Cybersecurity-BaronLLM_Offensive_Security_LLM_Q6_K_GGUF"
OLLAMA_API_BASE = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434")
OLLAMA_TIMEOUT_S = int(os.environ.get("OLLAMA_TIMEOUT_S", "180"))

USE_MCP = os.environ.get("USE_MCP", "0") == "1"
MCP_API_BASE = os.environ.get("MCP_API_BASE", OLLAMA_API_BASE)
MCP_API_KEY = os.environ.get("MCP_API_KEY", "")

# Config values we set – store them explicitly since lm doesn't expose them
TEMPERATURE = 0.45
MAX_TOKENS = 2048

lm = None

# Preferred: Ollama via OpenAI-compatible endpoint
try:
    lm = dspy.LM(
        model=f"ollama_chat/{OLLAMA_MODEL_NAME}",
        api_base=OLLAMA_API_BASE,
        api_key="ollama",  # Dummy key – required by OpenAI client but ignored by Ollama
        model_type="chat",
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        timeout=OLLAMA_TIMEOUT_S
    )
    print(f"[LLM] Connected to Ollama model '{OLLAMA_MODEL_NAME}' at {OLLAMA_API_BASE}")
except Exception as e:
    print(f"[LLM] Ollama connection failed: {e}")

# Fallbacks
if lm is None:
    if USE_MCP and MCP_API_BASE:
        try:
            print(f"[LLM] Using MCP proxy at {MCP_API_BASE}")
            lm = dspy.LM(DEFAULT_LLM, api_base=MCP_API_BASE, api_key=MCP_API_KEY)
        except Exception as e:
            print(f"[LLM] MCP failed: {e}")

    if lm is None:
        print(f"[LLM] Falling back to generic LM: {DEFAULT_LLM}")
        lm = dspy.LM(
            DEFAULT_LLM,
            api_base=os.environ.get("LLM_API_BASE", ""),
            api_key=os.environ.get("LLM_API_KEY", ""),
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )

dspy.configure(lm=lm)

# Safe print – no attribute access
print(f"[LLM] Configured successfully")
print(f"  - Model: {OLLAMA_MODEL_NAME}")
print(f"  - Temperature: {TEMPERATURE}")
print(f"  - Max tokens: {MAX_TOKENS}")
print(f"  - Timeout: {OLLAMA_TIMEOUT_S}s")
if 'q6_k' in OLLAMA_MODEL_NAME.lower() or 'gguf' in OLLAMA_MODEL_NAME.lower():
    print("[LLM] Using Q6_K GGUF quantization – optimized for Mac inference")

class BaseRedAgent(dspy.Module):
    """
    The parent class that all Red Team agents inherit from.
    Handles logging and shared configuration.
    """
    def __init__(self, agent_name, role_description):
        super().__init__()
        self.agent_name = agent_name
        self.role = role_description
        self.facts = (
            "Stapler 1 facts: Ports 21 (FTP anon login allowed, vsftpd 2.3.4 backdoor possible), "
            "80/12380 (WordPress with Advanced Video Embed plugin vulnerable to LFI for reading wp-config.php or /etc/passwd), "
            "139/445 (SMB null/guest sessions for share enum, leaked creds in backups), "
            "666 (custom service with potential buffer overflow). "
            "No CVE-2010-1671 or DocumentTemplateMethod exploit exists. "
            "Priv esc: Kernel CVE-2017-16995 (ebpf_mapfd_doubleput), sudo misconfigs, cron jobs."
        )
    
    def log(self, message):
        print(f"[{self.agent_name}] {message}")

    def report_error(self, error_msg):
        print(f"❌ [{self.agent_name} ERROR] {error_msg}")

    def vet_action(self, action):
        # Placeholder – expand with real boundary logic later
        if action is None:
            return None
        return action  # Assume safe for now