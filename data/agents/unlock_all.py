# -*- coding: utf-8 -*-
import os
import sys
import stat
import glob
import json

# 이 스크립트는 partner_guard.py와 잠금/해제 로직을 공유합니다.
# partner_guard.py의 해당 함수들과 동기화되어야 합니다.

# 색상 코드 (간단한 피드백용)
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
CYAN = "\033[96m"

# 경로 설정
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ACL_FILE = os.path.join(PROJECT_ROOT, 'AI_CORE', 'LOGS', 'ACL.json')

def set_readonly(path, make_readonly):
    """단일 파일/디렉토리의 읽기 전용 속성 설정/해제"""
    try:
        mode = os.stat(path).st_mode
        if make_readonly:
            os.chmod(path, mode & ~stat.S_IWRITE)
        else:
            os.chmod(path, mode | stat.S_IWRITE)
        return True
    except Exception:
        # 이 스크립트는 실패 시 조용히 넘어가는 것이 더 안정적일 수 있음
        return False

def _process_lock_paths(paths, make_readonly):
    """경로 목록에 대해 재귀적으로 잠금/해제 처리 (무시할 디렉토리 지정)"""
    processed_count = 0
    ignore_dirs = set(['node_modules', '.git', '.venv', '__pycache__', 'dist', 'build'])
    
    expanded_targets = set()
    for target in paths:
        if '*' in target or '?' in target:
            glob_path = os.path.join(PROJECT_ROOT, target)
            for p in glob.glob(glob_path, recursive=True):
                expanded_targets.add(p)
        else:
            expanded_targets.add(os.path.normpath(os.path.join(PROJECT_ROOT, target.replace('/', os.sep))))

    for path in expanded_targets:
        if not os.path.exists(path):
            continue

        # 처리 전에 무시할 디렉토리인지 확인
        if os.path.basename(path) in ignore_dirs:
            continue

        processed_count += 1
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path, topdown=True):
                # 하위 디렉토리 순회 자체를 막음
                dirs[:] = [d for d in dirs if d not in ignore_dirs]
                
                for name in files:
                    set_readonly(os.path.join(root, name), make_readonly)
                for name in dirs: # dirs 리스트는 위에서 필터링 되었음
                    set_readonly(os.path.join(root, name), make_readonly)
        
        # 마지막으로 자기 자신 처리
        set_readonly(path, make_readonly)
        
    return processed_count

def release_all_locks():
    """ACL.json에 정의된 모든 보호 대상을 물리적으로 잠금 해제 (-r)"""
    print(f"{CYAN}[UNLOCK] Releasing all sanctuary locks...{RESET}")
    try:
        if not os.path.exists(ACL_FILE): 
            print(f"{RED}[UNLOCK] ACL.json not found. Cannot release locks.{RESET}")
            return

        with open(ACL_FILE, 'r', encoding='utf-8') as f:
            acl = json.load(f)
        
        targets = set(acl.get("forbidden_all", []))
        for role in acl.get("roles", {}).values():
            targets.update(role.get("write_access", []))

        released_count = _process_lock_paths(targets, make_readonly=False)
        
        if released_count > 0:
            print(f"{GREEN}[UNLOCK] {released_count} sanctuary targets unlocked.{RESET}")
        else:
            print(f"{GREEN}[UNLOCK] No active locks found to release.{RESET}")

    except Exception as e:
        print(f"{RED}[UNLOCK] An error occurred during lock release: {e}{RESET}")

if __name__ == "__main__":
    # 윈도우에서 UTF-8 출력 강제
    if os.name == 'nt':
        sys.stdout.reconfigure(encoding='utf-8')
        
    release_all_locks()
