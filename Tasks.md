Tasks For Capstone

Red Team

Sam Tasks
    - [ ] Develop subagents 
    - [ ] Log agent actions
    - [ ] Designate tools for subagents

	Ryan Tasks
    - [ ] Develop MCP
        - [ ]  AI-Powered MCP Cybersecurity Automation Platform: https://github.com/0x4m4/hexstrike-ai/ 
        - [ ] AI-Powered Dark Web OSINT Tool: https://github.com/apurvsinghgautam/robin 
        - [ ] Integrate more external resources for agents to have more knowledge on current exploits, Threat landscape

	Joint Tasks
        - [ ]  Develop small scale team to be dockerized and run on limited hardware without extensive GPU Resources
        - [ ] Set up VM on bridged network to have Red team perform attack
        - [ ] Define metrics to be tested for industry use, AI performance etc.
        - [ ] Figure out how red team will perform in a scope of work similar to how bug bounties are performed and enterprise penitents (black, grey, white box attack)
        - [ ] AI Team needs to be able to have recursive learning abilities, track actions, provide a report and also output a risk assessment to the dashboard after 
        - [ ] Implement RAG (Retrieval-Augmented Generation) or a Memory Store (like ChromaDB or Faiss). When an agent tries an exploit and fails, it logs the failure to the vector DB. The next time it queries "how to attack port 80," it retrieves the context: "I already tried X and it failed."
        - [ ] You need a parsing step. Raw logs from tools like Robin or Nmap are messy. need a script (or agent task) that converts raw terminal output into a clean Markdown or JSON report for the dashboard.

Blue Team

	Mani Tasks
    - [ ] Implement ZySec-7B LLM 
        - [ ] https://huggingface.co/QuantFactory/SecurityLLM-GGUF 
    - [ ] Build orchestrator and Subagents for blue team 
    - [ ] Plan out how to secure blue team agents from being exploited

	Tony Tasks
    - [ ] Develop dashboard for blue team agents and how they will be deployed for small scale demo and

	Joint Tasks
    - [ ] Does the Blue Team block the attack or just report it?
    - [ ] Set up tail scale so agent can run on bridged network 


Potential Metrics to be tracked

Mean Time to Detect (MTTD): How long between the Red Team launching an exploit and the Blue Team logging it?

False Positive Rate: How often does the Blue Team scream "Hacker!" when the Red Team is just doing a harmless ping sweep?

Exploit Success Rate: (Red Team Metric) Number of successful shells / Number of vulnerabilities present.


Mani and Sam Tasks

    - [ ] Deploy VM on third device 
    - [ ] Set up tail scale environment for all 3 devices
    - [ ] Use portioner to manage all 3 
    - [ ] Deploy OWASP Juice Shop 
    - [ ] Do not mount a volume for the database. This is a feature, not a bug. It means every time you restart the container, the database wipes itself clean for the next demo.
    - [ ] Install Wazu
    - [ ] Create reset script so after pentest can reset for new one
    - [ ] Verify that logall_json is enabled in the Wazuh Manager (ossec.conf).

https://documentation.wazuh.com/current/installation-guide/wazuh-agent/index.html

Topology

Target Node
* Layer 1 (OS): Ubuntu Server + Tailscale + Wazuh Agent
* Layer 2 (Docker): Juice Shop Container
* The Wazuh Agent watches Layer 2



Infrastructure

The Attacker (M2 Mac)

The Datacenter (Mani's Proxmox): High-availability server, hosting the "Target" and "Blue Team".

The Observer (Sams Old iMac): dedicated "Mission Control" screen that runs Linux native (low overhead) just to display the Dashboard.