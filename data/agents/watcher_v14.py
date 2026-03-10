import os
import json
from base_agent_v14 import BaseAgentV14

def run_watcher():
    agents_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(agents_dir, "roles.json"), "r", encoding="utf-8") as f:
        roles = json.load(f)
    
    watcher_info = roles.get('watcher', {})
    agent = BaseAgentV14("watcher", watcher_info)
    agent.run()

if __name__ == "__main__":
    run_watcher()
