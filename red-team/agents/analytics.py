import json
import matplotlib.pyplot as plt
from datetime import datetime
import os

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "memory", "logs", "campaign_log.json")

def load_campaign_log():
    if not os.path.exists(LOG_FILE):
        print(f"Log file not found: {LOG_FILE}")
        return []
    entries = []
    with open(LOG_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON line: {line}")
    return entries

def plot_phase_timeline(log_entries):
    phases = []
    timestamps = []
    for entry in log_entries:
        if 'phase' in entry:
            phases.append(entry['phase'])
            ts = datetime.fromisoformat(entry['timestamp'])
            timestamps.append(ts)

    if not phases:
        print("No phase data to plot.")
        return

    # Plot timeline
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, range(len(phases)), marker='o')
    plt.yticks(range(len(phases)), phases)
    plt.xlabel('Time')
    plt.ylabel('Phase')
    plt.title('Campaign Phase Timeline')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('phase_timeline.png')
    plt.close()

def plot_phase_counts(log_entries):
    phase_counts = {}
    for entry in log_entries:
        phase = entry.get('phase', 'UNKNOWN')
        phase_counts[phase] = phase_counts.get(phase, 0) + 1

    if not phase_counts:
        print("No phase counts to plot.")
        return

    plt.figure(figsize=(8, 5))
    plt.bar(phase_counts.keys(), phase_counts.values())
    plt.xlabel('Phase')
    plt.ylabel('Count')
    plt.title('Phase Execution Counts')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('phase_counts.png')
    plt.close()

if __name__ == "__main__":
    log = load_campaign_log()
    if log:
        plot_phase_timeline(log)
        plot_phase_counts(log)
    else:
        print("No log data available.")