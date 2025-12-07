import nmap
import json
import os
import sys
from datetime import datetime

# CONFIGURATION
LOG_DIR = "memory/logs"

class RedTeamAgent:
    def __init__(self, target_ip):
        self.target_ip = target_ip
        self.nm = nmap.PortScanner()
        
        # Ensure log directory exists, handling the relative path correctly
        # This fixes issues where running from different folders breaks the path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.log_path = os.path.join(base_dir, LOG_DIR)
        os.makedirs(self.log_path, exist_ok=True)
        
        print(f"[*] Agent Initialized. Target: {self.target_ip}")

    def run_recon(self):
        """
        Runs a TCP SYN scan on common ports.
        Returns a structured dictionary of results.
        """
        print(f"[*] Starting Nmap Scan against {self.target_ip}...")
        
        try:
            # -sS: SYN Scan (Stealth), -T4: Aggressive timing, -p-: top 100 ports
            self.nm.scan(self.target_ip, arguments='-sS -T4 --top-ports 100')
            
            if self.target_ip not in self.nm.all_hosts():
                print(f"[!] Host {self.target_ip} seems DOWN.")
                return None

            host_data = self.nm[self.target_ip]
            clean_results = {
                "ip": self.target_ip,
                "status": host_data.state(),
                "open_ports": []
            }

            for proto in host_data.all_protocols():
                ports = sorted(host_data[proto].keys())
                for port in ports:
                    service = host_data[proto][port]
                    port_info = {
                        "port": port,
                        "protocol": proto,
                        "state": service['state'],
                        "service": service['name']
                    }
                    clean_results["open_ports"].append(port_info)
                    print(f"    -> FOUND: Port {port}/{proto} ({service['name']})")

            self.save_memory(clean_results)
            return clean_results

        except Exception as e:
            print(f"[!] Error during scan: {e}")
            return None

    def save_memory(self, data):
        """Saves the scan result to a JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.log_path}/scan_{self.target_ip}_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
            
        print(f"[*] Results saved to {filename}")

if __name__ == "__main__":
    agent = RedTeamAgent("127.0.0.1")
    agent.run_recon()