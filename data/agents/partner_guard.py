import os
import sys
import time
import psutil
import atexit
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
WHITE = "\033[97m"
BG_RED = "\033[41m"

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
PORT_FILE = os.path.join(DATA_DIR, 'partner_port.txt')
PID_FILE = os.path.join(DATA_DIR, 'partner_guard.pid') # PID 파일 추가
ACL_FILE = os.path.join(PROJECT_ROOT, 'AI_CORE', 'LOGS', 'ACL.json')

# 전역 상태
pending_response = None
input_event = threading.Event()
is_maintenance_mode = False

def cleanup():
    """종료 시 모든 빗장 해제 및 정화"""
    print(f"\n{YELLOW}[SHUTDOWN] Partner Guard Offline. Releasing locks...{RESET}")
    
    # ACL 파일을 읽어 모든 성역 해제 (-r)
    try:
        if os.path.exists(ACL_FILE):
            with open(ACL_FILE, 'r', encoding='utf-8') as f:
                acl = json.load(f)
            targets = acl.get("forbidden_all", [])
            for role in acl.get("roles", {}).values():
                targets.extend(role.get("write_access", []))
            
            for t in set(targets):
                full_path = os.path.join(PROJECT_ROOT, t.replace('/', os.sep))
                if os.path.exists(full_path):
                    # attrib -r 실행
                    subprocess.run(['attrib', '-r', os.path.normpath(full_path)], check=True, capture_output=True)
            print(f"{GREEN}[V] All physical locks released.{RESET}")
    except Exception as e:
        print(f"{RED}[!] Lock Release Failed: {e}{RESET}")

    if os.path.exists(PORT_FILE): os.remove(PORT_FILE)
    if os.path.exists(PID_FILE): os.remove(PID_FILE)

def signal_handler(sig, frame):
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
if os.name == 'nt': signal.signal(signal.SIGBREAK, signal_handler)
atexit.register(cleanup)

def get_approval_ui(tool, intent, level="YELLOW"):

def set_readonly(path, protect=True):
    if not os.path.exists(path): return
    flag = "+r" if protect else "-r"
    for i in range(3):
        try:
            subprocess.run(['attrib', flag, os.path.normpath(path)], check=True, capture_output=True)
            return True
        except: time.sleep(0.3)
    return False

def get_approval_ui(tool, intent, level="YELLOW"):
    """결재 UI 출력 및 키 입력 대기"""
    global pending_response
    os.system('cls')
    
    if level == "RED":
        print(f"{BG_RED}{WHITE}  [🚨 NUCLEAR ALERT] DESTRUCTIVE COMMAND BLOCKED!  {RESET}")
        print(f"{RED} This action is physically prohibited for AI sessions. {RESET}")
        color = RED
        can_approve = False
    else:
        print(f"{YELLOW}  [📋 WORK BRIEFING] Approval Required for Modification  {RESET}")
        color = YELLOW
        can_approve = True

    print(f"\n{CYAN} TOOL   :{RESET} {tool}")
    print(f"{CYAN} INTENT :{RESET} {color}{intent}{RESET}")
    print(f"\n{WHITE} ---------------------------------------------------- {RESET}")
    if can_approve:
        print(f" {GREEN}[SPACE] Approve{RESET}  |  {RED}[ESC] Deny & Stop{RESET}")
    else:
        print(f" {RED}[!] AI Forbidden to Execute. Press [ESC] to Cancel.{RESET}")
    print(f"{WHITE} ---------------------------------------------------- {RESET}")

    if not can_approve:
        # 핵버튼은 승인 절차 없이 키 입력만 확인 후 무조건 거절 반환
        while True:
            import msvcrt
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\x1b' or key == b' ': # ESC나 SPACE 아무거나 눌러도 상황 종료
                    return "DENIED"
            time.sleep(0.1)

    input_event.clear()
    input_event.wait()
    return pending_response

def keyboard_listener():
    """사령관님의 물리적 키 입력을 감시"""
    global pending_response, is_maintenance_mode
    import msvcrt
    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            # ESC (27), SPACE (32)
            if key == b' ':
                pending_response = "APPROVED"
                input_event.set()
            elif key == b'\x1b':
                pending_response = "DENIED"
                input_event.set()
            elif key.decode('utf-8').lower() == 'm':
                # 정비 모드 토글 (기존 가디언 기능 계승)
                is_maintenance_mode = not is_maintenance_mode
                print(f"\n{YELLOW}[SYSTEM] Maintenance Mode: {'ON' if is_maintenance_mode else 'OFF'}{RESET}")
        time.sleep(0.1)

def agent_handler(server_socket):
    """동반자 제미나이의 도구 사용 요청 처리"""
    while True:
        try:
            client, addr = server_socket.accept()
            data = client.recv(4096).decode('utf-8')
            if not data: continue
            
            req = json.loads(data)
            action = req.get("action")
            
            if action == "ASK_APPROVAL":
                tool = req.get("tool", "Unknown")
                intent = req.get("intent", "No reason provided")
                cmd = req.get("cmd", "").lower()
                
                # 핵버튼 감지 (Red Level)
                is_nuclear = any(k in cmd for k in ["restore", "reset --hard", "clean", "rm -rf", "del /s", "format"])
                level = "RED" if is_nuclear else "YELLOW"
                
                # 결재 진행
                result = get_approval_ui(tool, intent, level)
                
                if result == "APPROVED":
                    # 승인 시 파일 빗장 일시 해제 (대상 파일이 있다면)
                    target_file = req.get("file")
                    if target_file:
                        full_path = os.path.join(PROJECT_ROOT, target_file.replace('/', os.sep))
                        set_readonly(full_path, False)
                    
                    client.send(json.dumps({"status": "APPROVED"}).encode('utf-8'))
                    print(f"\n{GREEN}[V] Execution Authorized.{RESET}")
                else:
                    client.send(json.dumps({"status": "DENIED"}).encode('utf-8'))
                    print(f"\n{RED}[X] Execution Blocked by Sovereign.{RESET}")
            
            elif action == "FINISH_WORK":
                # 수정 완료 신호를 받으면 다시 잠금
                target_file = req.get("file")
                if target_file:
                    full_path = os.path.join(PROJECT_ROOT, target_file.replace('/', os.sep))
                    set_readonly(full_path, True)
                    print(f"{CYAN}[LOCK]{RESET} Sanctuary Re-sealed: {target_file}")
                client.send(json.dumps({"status": "OK"}).encode('utf-8'))

            client.close()
        except: break

def main():
    os.system('cls')
    # 1. PID 기록
    with open(PID_FILE, 'w') as f: f.write(str(os.getpid()))
    
    # 2. 서버 포트 준비
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 0))
    server.listen(1)
    port = server.getsockname()[1]
    with open(PORT_FILE, 'w') as f: f.write(str(port))

    print(f"{MAGENTA}===================================================={RESET}")
    print(f"{MAGENTA}   🛡️  PROJECT FREEISM: PARTNER GUARD V24.1{RESET}")
    print(f"{MAGENTA}===================================================={RESET}")
    print(f"{CYAN} STATUS      : {GREEN}SOVEREIGN EYE ACTIVE{RESET}")
    print(f"{CYAN} BEACON PORT : {port}{RESET}")
    print(f"{YELLOW} NOTICE      : Waiting for Partner Session...{RESET}")
    print(f"{MAGENTA}===================================================={RESET}\n")

    threading.Thread(target=keyboard_listener, daemon=True).start()
    agent_handler(server)

if __name__ == "__main__":
    try: main()
    finally:
        if os.path.exists(PORT_FILE): os.remove(PORT_FILE)
