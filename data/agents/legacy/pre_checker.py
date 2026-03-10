import os
import json
import shutil

# 설정 로드
RULES_PATH = os.path.join("data", "agents", "rules.json")
CONSENT_FILE = os.path.join("data", "agents", "consent.txt")
BACKUP_DIR = os.path.join("data", "backups")

if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

with open(RULES_PATH, "r", encoding="utf-8") as f:
    RULES = json.load(f)["council_laws"]

def create_snapshot(file_path):
    """작업 실행 직전, 파일의 '깨끗한 상태'를 스냅샷으로 저장합니다."""
    if os.path.exists(file_path):
        filename = os.path.basename(file_path)
        backup_path = os.path.join(BACKUP_DIR, f"{filename}.bak")
        shutil.copy2(file_path, backup_path)
        print(f"📸 Snapshot created: {backup_path}")
        return True
    return False

def pre_check(target_file=None):
    """작업 실행 전 파트너님의 승인 여부와 무결성을 최종 점검합니다."""
    print("\n🔍 Pre-Checker: Inspecting the proposal before execution...")

    # 1. 서면 동의 확인
    if not os.path.exists(CONSENT_FILE):
        print("🛑 [CRITICAL] No consent file found. Partner's written command is missing.")
        return False
    
    with open(CONSENT_FILE, "r", encoding="utf-8") as f:
        consent = f.read().strip()
    
    if not consent:
        print("🛑 [CRITICAL] Consent file is empty. Execution blocked.")
        return False
    
    print(f"✅ Partner's Command Found: '{consent}'")

    # 2. 스냅샷 생성 (가장 중요)
    if target_file:
        create_snapshot(target_file)
    
    return True

if __name__ == "__main__":
    # 테스트 시에는 인자로 대상 파일을 받을 수 있음
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else None
    if pre_check(target):
        print("🚀 [APPROVED] You are authorized to proceed.")
    else:
        sys.exit(1)
