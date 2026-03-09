import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from base_agent import run_agent

if __name__ == "__main__":
    # 메인 AI의 목소리를 대시보드에 직접 전달하는 전용 에이전트
    run_agent("MainAI", "전략 사령관의 파트너, 메인 AI (대시보드 전용 보이스)")
