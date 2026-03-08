import sys
import os
# 에이전트 스크립트가 위치한 디렉토리를 파이썬 경로에 추가하여 base_agent 임포트 보장
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from base_agent import run_agent
if __name__ == "__main__":
    run_agent("Watcher", "전지적 워처 (헌법 수호 및 감시)")
