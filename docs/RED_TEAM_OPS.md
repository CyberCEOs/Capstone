# Red Team Ops

# Red Team Development Plan
**Mission:** Autonomously penetrate the Enterprise VM and attempt to subvert the Blue Team Defense.

## 🛠 Tech Stack
* **Language:** Python 3.10+
* **Orchestration:** Custom Multi-Agent System (or LangChain/DSPy).
* **Tooling Protocol:** Model Context Protocol (MCP).
* **Core Tools:** Nmap, Hexstrike-AI, Robin (OSINT), Metasploit (via RPC).
* **Memory:** ChromaDB (Vector Store for RAG).

## 📋 Task List

### Phase 1: Core Agent Logic (Sam)
- [ ] **Recon Agent:** - Build `ReconAgent` class that accepts a Target IP.
    - Integrate `nmap` output parsing (XML/JSON -> LLM readable text).
- [ ] **Memory System:** - Setup ChromaDB to store "Successful Attacks."
    - Logic: *Before running an exploit, query DB: "Did this fail before?"*

### Phase 2: Tooling & MCP (Ryan)
- [ ] **MCP Server:** - Create a standard interface for Python tools so the AI can "call" them.
- [ ] **Hexstrike Integration:** - Adapt `0x4m4/hexstrike-ai` to run as a headless sub-process.
- [ ] **OSINT Feeds:** - Integrate `robin` to pull known CVE data for identified services.

### Phase 3: The "Anti-Blue" Logic (Joint)
- [ ] **Defense Detection:** - Create a prompt chain to specifically look for "Wazuh", "Ossec", or "Sysmon" processes.
- [ ] **Evasion/Poisoning:** - *Experimental:* If defense is found, generate "Noise" traffic to flood the Blue Team logs and trigger LLM hallucinations.

### Phase 4: Reporting
- [ ] **JSON Logger:** Ensure all actions output to `red-team/memory/logs/operations.json` for the Dashboard.