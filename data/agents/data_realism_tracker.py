import os
import re
import json
import time
from datetime import datetime

class DataRealismTracker:
    def __init__(self, project_root):
        self.project_root = project_root
        self.category_dir = os.path.join(project_root, "web", "src", "constants", "categories")
        self.domains = ["performance", "cinema", "exhibition", "broadcast", "festival", "education"]

    def analyze_domain(self, domain):
        file_path = os.path.join(self.category_dir, f"{domain}.ts")
        if not os.path.exists(file_path): return None

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # [DATA REALISM] L1-L6 노드 개수 정밀 집계
        # level: 2 (Trunk), level: 3 (Branch), level: 4 (Twig), level: 5 (Method), level: 6 (Fruit)
        stats = {
            "L1": 1, # Root (Domain itself)
            "L2": len(re.findall(r"level: 2", content)),
            "L3": len(re.findall(r"level: 3", content)),
            "L4": len(re.findall(r"level: 4", content)),
            "L5": len(re.findall(r"level: 5", content)),
            "L6": len(re.findall(r"level: 6", content)),
        }
        return stats

    def get_total_blueprint_status(self):
        overall = {}
        for domain in self.domains:
            stats = self.analyze_domain(domain)
            if stats: overall[domain] = stats
        return overall

    def report_to_hub(self):
        # 이 통계는 나중에 dashboard_api.py를 통해 대시보드에 실시간으로 전송됩니다.
        status = self.get_total_blueprint_status()
        return status

if __name__ == "__main__":
    # 독립 실행 테스트용
    tracker = DataRealismTracker(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    print(json.dumps(tracker.get_total_blueprint_status(), indent=2))
