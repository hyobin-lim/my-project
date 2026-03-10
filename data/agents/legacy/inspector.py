import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from base_agent import run_agent
if __name__ == "__main__":
    run_agent("Inspector", "전지적 인스펙터 (작업 결과 및 최종 무결성 검수)")
