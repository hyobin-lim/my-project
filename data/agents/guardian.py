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

def set_readonly(path, protect=True):
    """USB 지연을 고려한 재시도 로직이 포함된 attrib 설정"""
    if not os.path.exists(path): return
    flag = "+r" if protect else "-r"
    # USB 환경에서는 파일 잠금이 해제되는 데 시간이 걸릴 수 있으므로 재시도 수행
    for i in range(3):
        try:
            # 윈도우 attrib 명령어 실행 (경로 정규화 필수)
            subprocess.run(['attrib', flag, os.path.normpath(path)], check=True, capture_output=True)
            return True
        except:
            time.sleep(0.5)
    return False

def apply_global_protection(protect=True):
    """ACL 구역 전체 보호/해제 (USB 최적화)"""
    global is_maintenance_mode
    is_maintenance_mode = not protect
    
    try:
        if not os.path.exists(ACL_FILE): return
        with open(ACL_FILE, 'r', encoding='utf-8') as f:
            acl = json.load(f)
        
        targets = acl.get("forbidden_all", [])
        for role in acl.get("roles", {}).values():
            targets.extend(role.get("write_access", []))
        
        count = 0
        for t in set(targets):
            full_path = os.path.join(PROJECT_ROOT, t.replace('/', os.sep))
            if os.path.exists(full_path):
                if set_readonly(full_path, protect): count += 1
                
        status = f"{RED}PROTECTED{RESET}" if protect else f"{YELLOW}UNLOCKED{RESET}"
        print(f"[SYSTEM] Global Protection: {status} ({count} zones)")
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
    """실시간 파일 수정 감지 및 재잠금"""
    def on_modified(self, event):
        if event.is_directory: return
        abs_path = os.path.abspath(event.src_path)
        
        if abs_path in pending_unlocks:
            # 수정 완료 즉시 재잠금 (USB 지연 고려하여 약간의 대기 후 잠금도 고려 가능)
            if set_readonly(abs_path, protect=True):
                pending_unlocks.remove(abs_path)
                print(f"{CYAN}[GATE]{RESET} Re-locked: {os.path.basename(abs_path)}")

def agent_listener(server_socket):
    """에이전트 핸드셰이크 및 UNLOCK/PROSECUTE 요청 처리"""
    while True:
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
                    full_path = os.path.abspath(os.path.join(PROJECT_ROOT, file_rel_path.replace('/', os.sep)))
                    
                    if set_readonly(full_path, protect=False):
                        pending_unlocks.add(full_path)
                        print(f"{YELLOW}[UNLOCK]{RESET} Temporary access for: {file_rel_path}")
                        response = {"status": "UNLOCKED"}
                    else:
                        response = {"status": "ERROR", "reason": "USB/File Lock Failure"}
                
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
        except: break

def keyboard_monitor():
    """사령관 정비 모드 (m 키)"""
    import msvcrt
    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8').lower()
            if key == 'm':
                if is_maintenance_mode:
                    apply_global_protection(protect=True)
                else:
                    apply_global_protection(protect=False)
        time.sleep(0.1)

def cleanup():
    """종료 시 모든 빗장 해제 (유언장 로직)"""
    # 가디언이 수동으로 종료될 때만 빗장을 풉니다. (리부트 시에는 유지)
    print(f"\n{YELLOW}[SHUTDOWN] Sovereign takes control. Releasing all locks...{RESET}")
    apply_global_protection(protect=False)
    if os.path.exists(PORT_FILE): os.remove(PORT_FILE)
    if os.path.exists(PID_FILE): os.remove(PID_FILE)

# 윈도우 창 닫기 버튼(X) 대응을 위한 핸들러 (pywin32 미설치 대비 시그널 활용)
def signal_handler(sig, frame):
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler) # 종료 요청
# Windows에서 창 닫기 시 발생하는 시그널
if os.name == 'nt':
    signal.signal(signal.SIGBREAK, signal_handler)

atexit.register(cleanup)

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # 1. 인프라 준비
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    with open(PID_FILE, 'w') as f: f.write(str(os.getpid()))
    
    # 2. 서버 오픈
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 0))
    server_socket.listen(10)
    assigned_port = server_socket.getsockname()[1]
    with open(PORT_FILE, 'w') as f: f.write(str(assigned_port))
    
    # 3. 초기 보호 적용
    apply_global_protection(protect=True)
    
    print(f"{MAGENTA}===================================================={RESET}")
    print(f"{MAGENTA}   🛡️  PROJECT FREEISM: AGENT GUARDIAN V24.1{RESET}")
    print(f"{MAGENTA}===================================================={RESET}")
    print(f"{CYAN} STATUS      : {GREEN}PHYSICAL ENFORCER ACTIVE{RESET}")
    print(f"{CYAN} BEACON PORT : {assigned_port}{RESET}")
    print(f"{YELLOW} MODE        : [m] Maintenance Toggle{RESET}")
    print(f"{GRAY}* Monitoring territory violations (SIGKILL ready)...{RESET}")
    print(f"{MAGENTA}===================================================={RESET}\n")
    
    # 4. 스레드 시작
    threading.Thread(target=agent_listener, args=(server_socket,), daemon=True).start()
    threading.Thread(target=keyboard_monitor, args=(), daemon=True).start()
    
    observer = Observer()
    observer.schedule(SanctuaryHandler(), PROJECT_ROOT, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(5) # 체크 주기 완화 (USB 부하 방지)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
