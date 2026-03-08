import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from base_agent import run_agent
if __name__ == "__main__":
    run_agent("Debater", "전지적 디베이터 (비판적 대안 및 전략 제안)")
