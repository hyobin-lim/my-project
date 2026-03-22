import os
import sys
import time
import json
import socket
import threading
import subprocess
import signal
import atexit
import stat
import glob

# 색상 코드 (안전한 표준 코드만 사용)
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
PID_FILE = os.path.join(DATA_DIR, 'partner_guard.pid')
ACL_FILE = os.path.join(PROJECT_ROOT, 'AI_CORE', 'LOGS', 'ACL.json')

# 전역 상태
pending_response = None
input_event = threading.Event()
is_maintenance_mode = False
running = True

def cleanup():
    """종료 시 정화 작업"""
    global running
    running = False
    release_all_locks()
    if os.path.exists(PORT_FILE): 
        try: os.remove(PORT_FILE)
        except: pass
    if os.path.exists(PID_FILE): 
        try: os.remove(PID_FILE)
        except: pass

def signal_handler(sig, frame):
    """X 버튼 또는 Ctrl+C 감지"""
    cleanup()
    os._exit(0) # 즉각 강제 종료 (atexit은 os._exit에서 작동 안 하므로 직접 호출)

# 시그널 및 종료 핸들러 등록
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
if os.name == 'nt':
    try:
        signal.signal(signal.SIGBREAK, signal_handler)
    except:
        pass

def set_readonly(path, make_readonly):
    """단일 파일/디렉토리의 읽기 전용 속성 설정/해제"""
    try:
        mode = os.stat(path).st_mode
        if make_readonly:
            os.chmod(path, mode & ~stat.S_IWRITE)
        else:
            os.chmod(path, mode | stat.S_IWRITE)
        return True
    except Exception as e:
        print(f"{RED}[WARN] Perm fail on {os.path.basename(path)}: {e}{RESET}")
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
    print(f"\n{CYAN}[INIT] Releasing physical locks for all sanctuaries...{RESET}")
    try:
        if not os.path.exists(ACL_FILE): return

        with open(ACL_FILE, 'r', encoding='utf-8') as f:
            acl = json.load(f)
        
        targets = set(acl.get("forbidden_all", []))
        for role in acl.get("roles", {}).values():
            targets.update(role.get("write_access", []))

        released_count = _process_lock_paths(targets, make_readonly=False)
        
        if released_count > 0:
            print(f"{GREEN}[V] {released_count} sanctuary targets physically released.{RESET}")
    except Exception as e:
        print(f"{RED}[!] Lock Release Failed: {e}{RESET}")

def lock_all_sanctuaries():
    """ACL.json에 정의된 모든 보호 대상을 물리적으로 잠금 (+r)"""
    print(f"\n{CYAN}[INIT] Engaging physical locks for all sanctuaries...{RESET}")
    try:
        if not os.path.exists(ACL_FILE): return

        with open(ACL_FILE, 'r', encoding='utf-8') as f:
            acl = json.load(f)
        
        targets = set(acl.get("forbidden_all", []))
        for role in acl.get("roles", {}).values():
            targets.update(role.get("write_access", []))

        locked_count = _process_lock_paths(targets, make_readonly=True)
        
        if locked_count > 0:
            print(f"{GREEN}[V] {locked_count} sanctuary targets physically secured.{RESET}")
    except Exception as e:
        print(f"{RED}[!] Initialization Failed: {e}{RESET}")

def get_approval_ui(tool, intent, level="YELLOW"):
    """결재 UI 출력"""
    global pending_response
    if not running: return "DENIED"
    print("\n" * 2) # 화면 밀어내기
    
    if level == "RED":
        print(f"{BG_RED}{WHITE}  [ 핵폭발 경고 ] 파괴적인 명령이 차단되었습니다  {RESET}")
        print(f"{RED} 이 작업은 AI에게 물리적으로 금지되어 있습니다. {RESET}")
        color = RED
        can_approve = False
    else:
        print(f"{YELLOW}  [ 작업 브리핑 ] 파일 수정을 위한 승인이 필요합니다  {RESET}")
        color = YELLOW
        can_approve = True

    print(f"\n{CYAN} 도구   :{RESET} {tool}")
    safe_intent = str(intent).encode('utf-8', errors='replace').decode('utf-8')
    print(f"{CYAN} 의도   :{RESET} {color}{safe_intent}{RESET}")
    print(f"\n{WHITE} ---------------------------------------------------- {RESET}")
    if can_approve:
        print(f" {GREEN}[SPACE] 승인{RESET}  |  {RED}[ESC] 거부 및 중단{RESET}")
    else:
        print(f" {RED}[!] 금지됨. [ESC]를 눌러 취소하십시오.{RESET}")
    print(f"{WHITE} ---------------------------------------------------- {RESET}")

    if not can_approve:
        while True:
            import msvcrt
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\x1b' or key == b' ': return "DENIED"
            time.sleep(0.1)

    input_event.clear()
    input_event.wait()
    return pending_response

def keyboard_listener():
    """물리적 키 입력 감시"""
    global pending_response, is_maintenance_mode, running
    import msvcrt
    while running:
        try:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b' ':
                    pending_response = "APPROVED"
                    input_event.set()
                elif key == b'\x1b': # ESC 키
                    print(f"\n{RED}[SHUTDOWN] ESC 눌림. 가디언을 종료합니다...{RESET}")
                    cleanup()
                    os._exit(0)
                elif key.lower() == b'm':
                    is_maintenance_mode = not is_maintenance_mode
                    print(f"\n{YELLOW}[시스템] 정비 모드: {'켬' if is_maintenance_mode else '끔'}{RESET}")
        except:
            pass
        time.sleep(0.1)

def agent_handler(server_socket):
    """제미나이 요청 처리"""
    server_socket.settimeout(1.0) # 1초마다 타임아웃을 발생시켜 종료 플래그 확인
    while running:
        try:
            client, addr = server_socket.accept()
            raw_data = client.recv(4096)
            if not raw_data: continue
            
            req = json.loads(raw_data.decode('utf-8', errors='replace'))
            action = req.get("action")
            
            if action == "ASK_APPROVAL":
                tool = req.get("tool", "Unknown")
                intent = req.get("intent", "의도를 파악할 수 없습니다")
                cmd = str(req.get("cmd", "")).lower()
                is_nuclear = any(k in cmd for k in ["restore", "reset --hard", "clean", "rm -rf", "del /s", "format"])
                level = "RED" if is_nuclear else "YELLOW"
                
                result = get_approval_ui(tool, intent, level)
                
                if result == "APPROVED":
                    target_file = req.get("file")
                    if target_file:
                        set_readonly(os.path.join(PROJECT_ROOT, target_file.replace('/', os.sep)), False)
                    client.send(json.dumps({"status": "APPROVED"}).encode('utf-8'))
                else:
                    client.send(json.dumps({"status": "DENIED"}).encode('utf-8'))
            
            elif action == "FINISH_WORK":
                target_file = req.get("file")
                if target_file:
                    set_readonly(os.path.join(PROJECT_ROOT, target_file.replace('/', os.sep)), True)
                client.send(json.dumps({"status": "OK"}).encode('utf-8'))

            client.close()
        except socket.timeout:
            continue
        except Exception as e:
            if running: print(f"{RED}[오류] 에이전트 핸들러: {e}{RESET}")
            try: client.close()
            except: pass

def main():
    # 윈도우 환경 최적화 (인코딩 및 제목)
    if os.name == 'nt':
        import ctypes
        kernel32 = ctypes.windll.kernel32
        # ANSI 활성화
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        # 제목 설정 (글자 깨짐 방지)
        kernel32.SetConsoleTitleW("PARTNER GUARD V24.2")
    
    # PID 및 서버 기동
    with open(PID_FILE, 'w', encoding='utf-8') as f: f.write(str(os.getpid()))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 0))
    server.listen(1)
    port = server.getsockname()[1]
    with open(PORT_FILE, 'w', encoding='utf-8') as f: f.write(str(port))

    print(f"{MAGENTA}===================================================={RESET}")
    print(f"{MAGENTA}    PROJECT FREEISM: PARTNER GUARD V24.2{RESET}")
    print(f"{MAGENTA}===================================================={RESET}")
    print(f"{CYAN} 상태       : {GREEN}주권자의 눈 활성화 (가동 중){RESET}")
    print(f"{CYAN} 신호 포트   : {port}{RESET}")
    print(f"{YELLOW} 알림       : 주권자의 명령을 기다리는 중...{RESET}")
    print(f"{MAGENTA}===================================================={RESET}\n")

    # 초기 잠금 실행
    lock_all_sanctuaries()

    print(f"\n{GREEN}[완료] 모든 구역의 물리적 봉인이 완료되었습니다.{RESET}")
    print(f"{CYAN}[대기] 주권자(Gemini)의 신호를 기다리는 중입니다... (ESC: 종료){RESET}\n", flush=True)

    threading.Thread(target=keyboard_listener, daemon=True).start()
    agent_handler(server)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cleanup()
    except Exception as e:
        if running: print(f"{RED}[CRITICAL] Guard Failed: {e}{RESET}")
        cleanup()
    finally:
        if running: cleanup()
