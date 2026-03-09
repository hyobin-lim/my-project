import os
import json
from base_agent_v14 import BaseAgentV14

def run_inspector():
    agents_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(agents_dir, "roles.json"), "r", encoding="utf-8") as f:
        roles = json.load(f)
    
    info = roles.get('inspector', {})
    agent = BaseAgentV14("inspector", info)
    agent.run()

if __name__ == "__main__":
    run_inspector()
