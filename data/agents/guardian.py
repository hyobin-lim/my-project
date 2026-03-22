import os
import sys
import time
import psutil
import atexit
import signal
import socket
import json
import threading
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 색상 코드
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
GRAY = "\033[90m"

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
PID_FILE = os.path.join(DATA_DIR, 'guardian.pid')
PORT_FILE = os.path.join(DATA_DIR, 'port.txt')
ACL_FILE = os.path.join(PROJECT_ROOT, 'AI_CORE', 'LOGS', 'ACL.json')
STRIKE_FILE = os.path.join(PROJECT_ROOT, 'AI_CORE', 'LOGS', 'STRIKE_LEDGER.jsonl')

# BIOS 매뉴얼 경로 매핑
BIOS_MAP = {
    "T1": os.path.join(PROJECT_ROOT, "AI_CORE", "T1_EXECUTOR.md"),
    "T2": os.path.join(PROJECT_ROOT, "AI_CORE", "T2_COORDINATOR.md")
}

# 상태 관리
active_agents = {}
is_maintenance_mode = False
pending_unlocks = set()
pending_response = None
input_event = threading.Event()
running = True

import stat
import glob

# ... (기존 색상 코드 및 경로 설정 유지) ...

# 전역 상태
active_agents = {}
is_maintenance_mode = False
pending_unlocks = set()
pending_response = None
input_event = threading.Event()
running = True

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
        return False

def _process_lock_paths(paths, make_readonly):
    """경로 목록에 대해 재귀적으로 잠금/해제 처리 (무시할 디렉토리 지정)"""
    processed_count = 0
    ignore_dirs = set(['node_modules', '.git', '.venv', '__pycache__', 'dist', 'build', '.next', 'out'])
    
    expanded_targets = set()
    for target in paths:
        if '*' in target or '?' in target:
            glob_path = os.path.join(PROJECT_ROOT, target)
            for p in glob.glob(glob_path, recursive=True):
                expanded_targets.add(p)
        else:
            # 루트(./) 처리 시 공백 제거 및 경로 정규화
            clean_target = target.strip().replace('/', os.sep)
            expanded_targets.add(os.path.normpath(os.path.join(PROJECT_ROOT, clean_target)))

    for path in expanded_targets:
        if not os.path.exists(path): continue
        if os.path.basename(path) in ignore_dirs: continue

        processed_count += 1
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path, topdown=True):
                dirs[:] = [d for d in dirs if d not in ignore_dirs]
                for name in files: set_readonly(os.path.join(root, name), make_readonly)
                for name in dirs: set_readonly(os.path.join(root, name), make_readonly)
        set_readonly(path, make_readonly)
    return processed_count

def apply_global_protection(protect=True):
    """ACL 구역 전체 보호/해제"""
    global is_maintenance_mode
    is_maintenance_mode = not protect
    
    try:
        if not os.path.exists(ACL_FILE): return
        with open(ACL_FILE, 'r', encoding='utf-8') as f:
            acl = json.load(f)
        
        targets = set(acl.get("forbidden_all", []))
        for role in acl.get("roles", {}).values():
            targets.update(role.get("write_access", []))
        
        count = _process_lock_paths(targets, make_readonly=protect)
                
        status = f"{RED}PROTECTED{RESET}" if protect else f"{YELLOW}UNLOCKED{RESET}"
        print(f"[SYSTEM] Global Protection: {status} ({count} zones processed)")
    except Exception as e:
        print(f"{RED}[ERROR] Protection Failure: {e}{RESET}")

def record_strike(role, reason, evidence):
    """STRIKE_LEDGER.jsonl에 위반 사례 기록"""
    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "role": role,
        "reason": reason,
        "evidence": evidence,
        "reporter": "GUARDIAN"
    }
    try:
        with open(STRIKE_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except: pass

class SanctuaryHandler(FileSystemEventHandler):
    """실시간 파일 수정 감지 및 재잠금 (무시 디렉토리 적용)"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ignore_dirs_set = set(['node_modules', '.git', '.venv', '__pycache__', 'dist', 'build'])
        # 경로 비교를 위해 정규화된 경로 조각으로 변환
        self.ignore_patterns = {f"/{d}/" for d in self.ignore_dirs_set}

    def on_modified(self, event):
        if not running or event.is_directory:
            return
        
        # 정규화된 경로로 변환하여 포함 여부 확인
        norm_path = event.src_path.replace("\\", "/")
        if any(pattern in norm_path for pattern in self.ignore_patterns):
            return

        abs_path = os.path.abspath(event.src_path)
        if abs_path in pending_unlocks:
            if set_readonly(abs_path, make_readonly=True):
                pending_unlocks.discard(abs_path)
                print(f"{CYAN}[GATE]{RESET} Re-locked: {os.path.basename(abs_path)}")

def get_approval_ui(role, tool, file_path):
    """실무자 작업에 대한 파트너 결재 UI"""
    global pending_response
    if not running: return "DENIED"
    print("\n" * 2)
    print(f"{YELLOW}  [ 에이전트 요청 ] {role}의 작업 승인이 필요합니다  {RESET}")
    print(f"\n{CYAN} 에이전트 :{RESET} {role}")
    print(f"{CYAN} 도구    :{RESET} {tool}")
    print(f"{CYAN} 대상    :{RESET} {YELLOW}{file_path}{RESET}")
    print(f"\n{WHITE} ---------------------------------------------------- {RESET}")
    print(f" {GREEN}[SPACE] 승인{RESET}  |  {RED}[ESC] 거부 및 에이전트 중단{RESET}")
    print(f"{WHITE} ---------------------------------------------------- {RESET}")

    input_event.clear()
    input_event.wait()
    return pending_response

def agent_listener(server_socket):
    """에이전트 핸드셰이크 및 UNLOCK/PROSECUTE 요청 처리"""
    server_socket.settimeout(1.0)
    while running:
        try:
            client, addr = server_socket.accept()
            data = client.recv(4096).decode('utf-8')
            if not data: continue
            
            try:
                request = json.loads(data)
                action = request.get("action", "HANDSHAKE")
                role = request.get("role", "UNKNOWN")
                
                if action == "HANDSHAKE":
                    agent_pid = int(request.get("pid", 0))
                    print(f"{GREEN}[HANDSHAKE]{RESET} {role} (PID: {agent_pid}) Linked.")
                    active_agents[agent_pid] = role
                    response = {"status": "APPROVED", "bios_path": BIOS_MAP.get(role, "UNKNOWN")}
                
                elif action == "UNLOCK":
                    file_rel_path = request.get("file")
                    tool = request.get("tool", "Modification")
                    full_path = os.path.abspath(os.path.join(PROJECT_ROOT, file_rel_path.replace('/', os.sep)))
                    
                    approval = get_approval_ui(role, tool, file_rel_path)
                    
                    if approval == "APPROVED":
                        if set_readonly(full_path, protect=False):
                            pending_unlocks.add(full_path)
                            print(f"{YELLOW}[UNLOCK]{RESET} Temporary access granted for {role}: {file_rel_path}")
                            response = {"status": "UNLOCKED"}
                        else:
                            response = {"status": "ERROR", "reason": "USB/File Lock Failure"}
                    else:
                        print(f"{RED}[DENIED]{RESET} Partner rejected {role}'s request.")
                        response = {"status": "DENIED"}
                
                elif action == "PROSECUTE":
                    target = request.get("target")
                    reason = request.get("reason")
                    evidence = request.get("evidence")
                    print(f"{RED}[INDICTMENT]{RESET} {role} prosecutes {target}: {reason}")
                    record_strike(target, reason, evidence)
                    response = {"status": "RECORDED"}
                
                client.send(json.dumps(response).encode('utf-8'))
            except: pass
            client.close()
        except socket.timeout:
            continue
        except Exception as e:
            if running: print(f"{RED}[ERROR] Agent Listener: {e}{RESET}")
            try: client.close()
            except: pass

def keyboard_monitor():
    """사령관 정비 모드 (m 키) 및 결재 처리/종료"""
    global pending_response, running, is_maintenance_mode
    import msvcrt
    while running:
        try:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b' ':
                    pending_response = "APPROVED"
                    input_event.set()
                elif key == b'\x1b': # ESC 키
                    print(f"\n{RED}[SHUTDOWN] ESC pressed. Terminating Guardian...{RESET}")
                    cleanup()
                    os._exit(0)
                elif key.decode('utf-8').lower() == 'm':
                    if is_maintenance_mode:
                        apply_global_protection(protect=True)
                    else:
                        apply_global_protection(protect=False)
        except:
            pass
        time.sleep(0.1)

def cleanup():
    """종료 시 모든 빗장 해제 (유언장 로직)"""
    global running
    if not running: return
    running = False
    print(f"\n{YELLOW}[SHUTDOWN] Sovereign takes control. Releasing all locks...{RESET}")
    apply_global_protection(protect=False)
    if os.path.exists(PORT_FILE): 
        try: os.remove(PORT_FILE)
        except: pass
    if os.path.exists(PID_FILE): 
        try: os.remove(PID_FILE)
        except: pass

def signal_handler(sig, frame):
    cleanup()
    os._exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
if os.name == 'nt':
    try:
        signal.signal(signal.SIGBREAK, signal_handler)
    except:
        pass

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    with open(PID_FILE, 'w', encoding='utf-8') as f: f.write(str(os.getpid()))
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 0))
    server_socket.listen(10)
    assigned_port = server_socket.getsockname()[1]
    with open(PORT_FILE, 'w', encoding='utf-8') as f: f.write(str(assigned_port))
    
    apply_global_protection(protect=True)
    
    print(f"\n{GREEN}[완료] 실무자 구역의 물리적 방화벽이 가동되었습니다.{RESET}")
    print(f"{CYAN}[감시] 실무자 AI(T1, T2)의 요청을 기다리는 중... (ESC: 종료){RESET}\n", flush=True)
    
    threading.Thread(target=agent_listener, args=(server_socket,), daemon=True).start()
    threading.Thread(target=keyboard_monitor, args=(), daemon=True).start()
    
    observer = Observer()
    observer.schedule(SanctuaryHandler(), PROJECT_ROOT, recursive=True)
    observer.start()
    
    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()
    finally:
        if running: cleanup()
        observer.stop()
        observer.join()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        if running: print(f"{RED}[CRITICAL] Guardian Failed: {e}{RESET}")
        cleanup()
