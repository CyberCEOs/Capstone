# Capstone
**Autonomous AI Adversarial Operations (Red vs. Blue)**

> **Status:** 🚧 In Development (Sprint 0)
> **Docs:** [Master Plan](docs/MASTER_PLAN.md) | [Red Ops](docs/RED_TEAM_OPS.md) | [Blue Ops](docs/BLUE_TEAM_OPS.md)

## 🎯 Project Overview
This project demonstrates an autonomous cybersecurity conflict between two AI systems:
1.  **Red Team:** A multi-agent system (Python/MCP) that autonomously reconnoiters and exploits vulnerabilities.
2.  **Blue Team:** An AI-integrated SIEM (Wazuh + ZySec-7B LLM) that monitors, detects, and reports on attacks in real-time.
3.  **Enterprise:** A mock corporate environment (Ubuntu/Juice Shop) serving as the battlefield.

## 🏗 Architecture
The system runs on a hybrid **Tailscale Mesh Network** bridging three physical nodes:

* **Node A (Sam's M2 Mac):** Hosts Red Team Agents & Blue Team Brain (LLM).
* **Node B (Mani's Proxmox):** Hosts the Enterprise VM (Target) & Wazuh Agent.
* **Node C (Sam's iMac):** Hosts the Central Dashboard (Observer).

## 📂 Repository Structure
This is a Monorepo. Please work ONLY in your designated team folder.

| Folder | Team | Description |
| :--- | :--- | :--- |
| `red-team/` | **Sam & Ryan** | Attack agents, Hexstrike integration, and Vector DB. |
| `blue-team/` | **Mani & Tony** | Wazuh rules, LLM orchestrator, and Defense logic. |
| `infrastructure/`| **Sam & Mani** | Docker Compose stacks, VM configs, and reset scripts. |
| `dashboard/` | **Tony** | Frontend visualization (React/Streamlit). |
| `docs/` | **All** | Architecture diagrams and planning documents. |

## 🚀 Getting Started

### 1. Clone & Branch
**DO NOT work on main.** Checkout your team branch immediately.
```bash
git clone [https://github.com/CyberCEOs/Capstone.git](https://github.com/CyberCEOs/Capstone.git)
cd Capstone

# Choose your fighter:
git checkout red/dev       # Red Team
git checkout blue/dev      # Blue Team
git checkout dashboard/dev # Dashboard
git checkout infra/dev     # Infrastructure
