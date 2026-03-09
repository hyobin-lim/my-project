import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from base_agent import run_agent
if __name__ == "__main__":
    run_agent("Guardian", "전지적 가디언 (오타, 생략, 기술적 무결성 수호)")
