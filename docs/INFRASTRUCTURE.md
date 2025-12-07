# Infrastructure

# Infrastructure & Networking
**Status:** Hybrid Deployment (Local + Cloud/Remote)

## 🗺 Topology Map
[Sam's M2 Mac] <===(Tailscale VPN)===> [Mani's Proxmox Server]
      |                                        |
(Red Team Agents)                       (Enterprise VM)
(Blue Team Brain)                       (Wazuh Agent)

## 🏗 The Environment

### 1. The Enterprise (Target)
* **Host:** Mani's Proxmox.
* **OS:** Ubuntu Server 22.04 LTS.
* **Services:**
    * **Juice Shop:** Running in Docker on Port 3000.
    * **Wazuh Agent:** Running on Host (monitoring Docker + System).
* **Networking:** * Must accept traffic on Port 3000 (HTTP) and 22 (SSH) from the Tailscale Interface `tailscale0`.

### 2. The Blue Stack (Defense Hub)
* **Host:** Sam's M2 Mac.
* **Container:** `wazuh/wazuh-docker` (Single Node).
* **Config:** * `WAZUH_MANAGER_IP` = Sam's Tailscale IP.

### 3. Networking Rules (Tailscale)
* **ACLs:** * Red Team (Sam) -> Allowed to access Ports 22, 80, 443, 3000 on Enterprise.
    * Enterprise (Mani) -> Allowed to access Port 1514 (Wazuh Registration) on Sam's M2.

## 🔄 Reset Workflow
To ensure repeatable demos, we need a "Clean Slate" script.

**Script:** `infrastructure/scripts/reset_demo.sh`
1. **Red:** Kill all Python agent processes. Clear `operations_log.json`.
2. **Blue:** Archive `alerts.json` (save as `run_1.log`). Restart Wazuh Manager.
3. **Enterprise:** SSH into Proxmox -> `docker restart juice-shop`.