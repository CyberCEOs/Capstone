# Blue Team Ops

# Blue Team Development Plan
**Mission:** Monitor the Enterprise VM, detect anomalies using Generative AI, and assist human analysts.

## 🛠 Tech Stack
* **SIEM:** Wazuh (Open Source).
* **AI Model:** ZySec-7B (GGUF Quantized).
* **Inference Engine:** Ollama (running on Sam's M2 Mac).
* **Visualization:** React/Streamlit (Dashboard).

## 📋 Task List

### Phase 1: The Eyes (Mani)
- [ ] **Wazuh Deployment:** - Deploy Wazuh Manager on Sam's M2 (Docker).
    - Deploy Wazuh Agent on Mani's Proxmox VM (Bare Metal).
- [ ] **Log Pipeline:** - Verify logs flow from Proxmox -> Tailscale -> M2 Mac.
    - Enable `logall_json` in `ossec.conf` to capture *everything*, not just alerts.

### Phase 2: The Brain (Mani)
- [ ] **LLM Integration:** - Write Python middleware (`orchestrator.py`) that watches `alerts.json`.
    - **Filter Logic:** Only send "Severity Level 10+" alerts to the LLM (to save tokens/speed).
    - **Prompt Engineering:** *System Prompt: "You are a Security Analyst. Analyze this JSON log. Is it a False Positive? Explain why."*

### Phase 3: The Dashboard (Tony)
- [ ] **Frontend Build:** - Create a web interface (Observer Node).
    - **Split Screen View:** Left side = Red Team Logs (Attack Stream), Right side = Blue Team Alerts (Defense Stream).
- [ ] **Metrics Calculation:** - Real-time display of "Attacks Launched" vs "Attacks Detected."

### Phase 4: Security
- [ ] **Hardening:** Ensure the Blue Team API is not easily accessible via default ports (secure the API keys).