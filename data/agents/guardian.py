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
import stat
import glob
import secrets
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
WHITE = "\033[97m"

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
is_waiting_approval = False
pending_unlocks = set()
pending_response = None
input_event = threading.Event()
running = True
current_tokens = {} # 각 에이전트별 토큰 관리
relock_timers = {} # 에이전트별 자동 봉인 타이머

def set_readonly(path, make_readonly):
    """파일 속성 설정"""
    try:
        mode = os.stat(path).st_mode
        if make_readonly: os.chmod(path, mode & ~stat.S_IWRITE)
        else: os.chmod(path, mode | stat.S_IWRITE)
        return True
    except: return False

def _process_lock_paths(paths, make_readonly):
    """일괄 잠금/해제 (동기식)"""
    processed = 0
    ignore = set(['node_modules', '.git', '.venv', '__pycache__', 'dist', 'build', '.next', 'out'])
    for target in paths:
        full_p = os.path.normpath(os.path.join(PROJECT_ROOT, target.strip().replace('/', os.sep)))
        if '*' in target or '?' in target:
            for p in glob.glob(full_p, recursive=True):
                if not any(ig in p for ig in ignore):
                    if not (p.endswith('.pid') or p.endswith('.txt')):
                        set_readonly(p, make_readonly)
                        processed += 1
        elif os.path.exists(full_p):
            if os.path.isdir(full_p):
                for root, dirs, files in os.walk(full_p):
                    dirs[:] = [d for d in dirs if d not in ignore]
                    for f in files:
                        if not (f.endswith('.pid') or f.endswith('.txt')):
                            set_readonly(os.path.join(root, f), make_readonly)
                            processed += 1
            else:
                if not (full_p.endswith('.pid') or full_p.endswith('.txt')):
                    set_readonly(full_p, make_readonly)
                    processed += 1
    return processed

def apply_global_protection(protect=True):
    """ACL 구역 전체 보호/해제"""
    status = "봉인" if protect else "해제"
    print(f"\n{CYAN}[{status}] 모든 구역을 물리적으로 {status} 중입니다...{RESET}", flush=True)
    sys.stdout.flush()
    try:
        if not os.path.exists(ACL_FILE): return
        with open(ACL_FILE, 'r', encoding='utf-8') as f: acl = json.load(f)
        targets = set(acl.get("forbidden_all", []))
        for role in acl.get("roles", {}).values(): targets.update(role.get("write_access", []))
        count = _process_lock_paths(targets, protect)
        print(f"{GREEN}[완료] {count}개의 구역이 {status}되었습니다.{RESET}", flush=True)
        sys.stdout.flush()
    except Exception as e:
        print(f"{RED}[오류] {status} 실패: {e}{RESET}", flush=True)
        sys.stdout.flush()

def auto_relock_task(role):
    """시간 초과 시 자동으로 빗장을 잠그는 콜백 (2분 규칙)"""
    global current_tokens
    if running:
        print(f"\n{RED}[보안] {role}의 작업 시간 초과(120초)로 인해 성역을 자동으로 재봉인했습니다.{RESET}", flush=True)
        sys.stdout.flush()
        apply_global_protection(protect=True)
        if role in current_tokens: del current_tokens[role]

def record_strike(role, reason, evidence):
    """스트라이크 장부 기록"""
    entry = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "role": role, "reason": reason, "evidence": evidence, "reporter": "PRISM_JUDGE"}
    try:
        with open(STRIKE_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except: pass

class SanctuaryHandler(FileSystemEventHandler):
    """자동 재잠금 파수꾼"""
    def on_modified(self, event):
        if not running or event.is_directory: return
        abs_p = os.path.abspath(event.src_path)
        if abs_p in pending_unlocks:
            if set_readonly(abs_p, True):
                pending_unlocks.discard(abs_p)
                print(f"{CYAN}[봉인]{RESET} {os.path.basename(abs_p)} 재봉인됨.", flush=True)
                sys.stdout.flush()

def get_approval_ui(role, tool, file_path, payload=""):
    """실무자용 내용물 검사 결재 UI (자동 회수 포함)"""
    global pending_response, is_waiting_approval
    if not running: return "DENIED"
    
    p_lower = str(payload).lower()
    is_nuclear = any(k in p_lower for k in ["restore", "reset --hard", "clean", "push -f", "push --force", "branch -d", "rm -rf", "rd /s", "del /s", "remove-item", "format"])
    is_self_update = file_path and any(f in file_path for f in ["partner_guard.py", "guardian.py"])
    is_lazy = False if is_self_update else any(k in p_lower for k in ["...", "(상동)", "(중략)", "unchanged", "rest of code"])
    
    can_approve = True
    status_msg = f"{role}의 작업 승인이 필요합니다"
    if is_nuclear:
        can_approve = False
        status_msg = f"{RED}[위험] {role}의 파멸적 명령어 감지 - 차단됨{RESET}"
    elif is_lazy:
        can_approve = False
        status_msg = f"{RED}[경고] {role}의 지능적 나태함(축약) 감지 - 차단됨{RESET}"

    print("\n" * 2, flush=True)
    print(f"{YELLOW}  [ 에이전트 요청 ] {status_msg}  {RESET}", flush=True)
    print(f"\n{CYAN} 에이전트 :{RESET} {role}")
    print(f"{CYAN} 도구    :{RESET} {tool}")
    print(f"{CYAN} 대상    :{RESET} {YELLOW}{file_path}{RESET}")
    
    if payload:
        preview = (payload[:150].replace('\n', ' ') + '...') if len(payload) > 150 else payload.replace('\n', ' ')
        print(f"{CYAN} 내용물  :{RESET} {WHITE}{preview}{RESET}")
        
    print(f"\n{WHITE} ---------------------------------------------------- {RESET}", flush=True)
    if can_approve:
        print(f" {GREEN}[SPACE] 승인{RESET}  |  {RED}[ESC] 거부 및 반려{RESET}", flush=True)
    else:
        print(f" {RED}[!] 사법적 위반으로 승인 불가. [ESC]로 반려하십시오.{RESET}", flush=True)
    print(f"{WHITE} ---------------------------------------------------- {RESET}", flush=True)
    sys.stdout.flush()

    is_waiting_approval = True
    input_event.clear()
    # 120초 자동 회수 (파트너님의 여유로운 검토 반영)
    is_timed_out = not input_event.wait(timeout=120.0)
    is_waiting_approval = False
    
    if is_timed_out:
        print(f"\n{RED}[타임아웃] 120초간 응답이 없어 작업을 자동 반려합니다.{RESET}", flush=True)
        sys.stdout.flush()
        pending_response = "DENIED"
    
    if pending_response == "APPROVED" and can_approve:
        print(f"\n{GREEN}[결정] 파트너가 승인했습니다. {role}에게 빗장을 개방합니다...{RESET}", flush=True)
    else:
        reason = "파트너 거부" if pending_response == "DENIED" else "사법적 차단"
        print(f"\n{RED}[반려] {reason}로 인해 {role}의 요청이 기각되었습니다.{RESET}", flush=True)
        pending_response = "DENIED"
    
    sys.stdout.flush()
    return pending_response

def agent_listener(server_socket):
    """실무자 요청 처리 (V25.3.6 자동 봉인 타이머 체계)"""
    global current_tokens, relock_timers
    server_socket.settimeout(1.0)
    decoder = json.JSONDecoder()
    while running:
        client = None
        try:
            client, addr = server_socket.accept()
            raw_data = client.recv(16384).decode('utf-8', errors='replace')
            if not raw_data: continue
            buffer = raw_data.strip()
            while buffer:
                try:
                    req, index = decoder.raw_decode(buffer)
                    buffer = buffer[index:].strip()
                    action = req.get("action", "HANDSHAKE")
                    role = req.get("role", "UNKNOWN")
                    
                    if action == "HANDSHAKE":
                        print(f"{GREEN}[연결]{RESET} {role} (PID: {req.get('pid')}) 사법 체계 편입.", flush=True)
                        sys.stdout.flush()
                        active_agents[int(req.get("pid", 0))] = role
                        response = {"status": "APPROVED", "bios_path": BIOS_MAP.get(role, "UNKNOWN")}
                    elif action == "UNLOCK":
                        full_path = os.path.normpath(os.path.join(PROJECT_ROOT, req.get("file").replace('/', os.sep)))
                        approval = get_approval_ui(role, req.get("tool", "Modification"), req.get("file"), req.get("payload", ""))
                        if approval == "APPROVED":
                            token = secrets.token_hex(4).upper()
                            current_tokens[role] = {"token": token, "tool": req.get("tool")}
                            if set_readonly(full_path, False):
                                pending_unlocks.add(full_path)
                                print(f"{YELLOW}[해방]{RESET} {role}에게 {req.get('file')} 권한 부여.", flush=True)
                                sys.stdout.flush()
                                
                                # [V25.3.6] 120초 자동 봉인 타이머 가동
                                if role in relock_timers: relock_timers[role].cancel()
                                relock_timers[role] = threading.Timer(120.0, auto_relock_task, args=[role])
                                relock_timers[role].start()
                                
                                response = {"status": "UNLOCKED", "token": token}
                            else: response = {"status": "ERROR", "reason": "Lock Failure"}
                        else: response = {"status": "DENIED"}
                    elif action == "VERIFY_TOKEN":
                        stored = current_tokens.get(role, {})
                        if stored.get("token") == req.get("token") and stored.get("tool") == req.get("tool"):
                            response = {"status": "VALID"}
                        else: response = {"status": "INVALID"}
                    elif action == "FINISH_WORK":
                        # [V25.3.6] 작업 종료 시 타이머 취소
                        if role in relock_timers:
                            relock_timers[role].cancel()
                            del relock_timers[role]
                        if role in current_tokens: del current_tokens[role]
                        response = {"status": "OK"}
                    elif action == "PROSECUTE":
                        record_strike(req.get("target"), req.get("reason"), req.get("evidence"))
                        response = {"status": "RECORDED"}
                    client.send(json.dumps(response).encode('utf-8'))
                except: break
            if client: client.close()
        except socket.timeout: continue
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            if client: 
                try: client.close()
                except: pass
            continue
        except Exception as e:
            if running: print(f"{RED}[경고] 본진 신경계 수신 지연: {e}{RESET}", flush=True)
            sys.stdout.flush()
            if client:
                try: client.close()
                except: pass

def keyboard_monitor():
    """실무자 가디언 키 감시 (ESC 이원화)"""
    global pending_response, running, is_waiting_approval
    import msvcrt
    while running:
        try:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b' ':
                    if is_waiting_approval:
                        pending_response = "APPROVED"
                        input_event.set()
                elif key == b'\x1b': # ESC 키
                    if is_waiting_approval:
                        pending_response = "DENIED"
                        input_event.set()
                    else:
                        cleanup()
                        os._exit(0)
        except: pass
        time.sleep(0.1)

def cleanup():
    """종료 시 모든 빗장 해제 및 보고 (동기식)"""
    global running
    if not running: return
    running = False
    print(f"\n{YELLOW}[SHUTDOWN] 가디언을 종료합니다.{RESET}", flush=True)
    apply_global_protection(False)
    for f in [PORT_FILE, PID_FILE]:
        if os.path.exists(f): 
            try: os.remove(f)
            except: pass
    print(f"\n{MAGENTA}[REPORT] 물리적 봉인 해제 완료. 이제 터미널 제어권을 반환합니다.{RESET}", flush=True)
    sys.stdout.flush()
    time.sleep(1)

def main():
    if os.name == 'nt':
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        kernel32.SetConsoleTitleW("PRISM JUDGE V25.3.6 (PRACTITIONER GUARD)")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 0))
    server.listen(10)
    with open(PORT_FILE, 'w', encoding='utf-8') as f: f.write(str(server.getsockname()[1]))
    with open(PID_FILE, 'w', encoding='utf-8') as f: f.write(str(os.getpid()))
    
    print(f"{CYAN}===================================================={RESET}", flush=True)
    print(f"{CYAN}    PROJECT FREEISM: PRISM JUDGE V25.3.6{RESET}", flush=True)
    print(f"{CYAN}===================================================={RESET}", flush=True)
    sys.stdout.flush()
    apply_global_protection(True)
    print(f"\n{GREEN}[완료] 실무자 구역의 물리적 방화벽이 가동되었습니다.{RESET}", flush=True)
    print(f"{CYAN}[감시] 실무자 AI(T1, T2)의 작업 신호를 대기 중...{RESET}\n", flush=True)
    sys.stdout.flush()
    
    threading.Thread(target=agent_listener, args=(server,), daemon=True).start()
    threading.Thread(target=keyboard_monitor, args=(), daemon=True).start()
    
    observer = Observer()
    observer.schedule(SanctuaryHandler(), PROJECT_ROOT, recursive=True)
    observer.start()
    try:
        while running: time.sleep(1)
    finally: cleanup(); observer.stop(); observer.join()

if __name__ == "__main__":
    try: main()
    except Exception as e:
        if running: print(f"{RED}[CRITICAL] Judge Failed: {e}{RESET}", flush=True)
        cleanup()
