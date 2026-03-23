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
import secrets

# 색상 코드
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
GRAY = "\033[90m"
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
is_waiting_approval = False
running = True
current_token = None
permitted_tool = None
relock_timer = None

def set_readonly(path, make_readonly):
    """파일의 읽기 전용 속성 설정/해제"""
    try:
        if not os.path.exists(path): return False
        mode = os.stat(path).st_mode
        if make_readonly: os.chmod(path, mode & ~stat.S_IWRITE)
        else: os.chmod(path, mode | stat.S_IWRITE)
        return True
    except: return False

def _process_lock_paths(paths, make_readonly):
    """경로 잠금/해제 처리 (진행률 표시 및 재귀적 스캔)"""
    processed_count = 0
    ignore_dirs = set(['node_modules', '.git', '.venv', '__pycache__', 'dist', 'build', '.next', 'out'])
    micro_opening_exts = ['.pid', '.txt']
    
    all_files = []
    for target in paths:
        clean_target = target.strip().replace('/', os.sep).lstrip(os.sep)
        full_p = os.path.normpath(os.path.join(PROJECT_ROOT, clean_target))
        if any(full_p.endswith(ext) for ext in micro_opening_exts): continue
        
        if os.path.isdir(full_p):
            for root, dirs, files in os.walk(full_p):
                dirs[:] = [d for d in dirs if d not in ignore_dirs]
                for file in files:
                    if any(file.endswith(ext) for ext in micro_opening_exts): continue
                    all_files.append(os.path.join(root, file))
        elif os.path.exists(full_p):
            all_files.append(full_p)

    total = len(all_files)
    if total == 0: return 0

    for i, file_path in enumerate(all_files):
        try:
            if set_readonly(file_path, make_readonly):
                processed_count += 1
            if (i + 1) % max(1, total // 10) == 0 or (i + 1) == total:
                percent = int(((i + 1) / total) * 100)
                status = "봉인" if make_readonly else "해방"
                print(f"\r{CYAN}[{status}] {percent}% 완료 ({i + 1}/{total})...{RESET}", end="", flush=True)
        except: continue
            
    print() # 줄바꿈
    return processed_count

def release_all_locks():
    """ACL 전 구역 잠금 해제"""
    print(f"\n{CYAN}[해방] 모든 물리적 봉인을 해제 중입니다...{RESET}", flush=True)
    sys.stdout.flush()
    try:
        if not os.path.exists(ACL_FILE): return
        with open(ACL_FILE, 'r', encoding='utf-8') as f: acl = json.load(f)
        targets = set(acl.get("forbidden_all", []))
        for role in acl.get("roles", {}).values(): targets.update(role.get("write_access", []))
        count = _process_lock_paths(targets, False)
        print(f"{GREEN}[완료] {count}개의 구역이 자유를 되찾았습니다.{RESET}", flush=True)
        sys.stdout.flush()
    except Exception as e:
        print(f"{RED}[오류] 봉인 해제 실패: {e}{RESET}", flush=True)
        sys.stdout.flush()

def lock_all_sanctuaries():
    """ACL 전 구역 물리적 봉인"""
    print(f"\n{CYAN}[봉인] 모든 구역을 물리적으로 보호합니다...{RESET}", flush=True)
    sys.stdout.flush()
    try:
        if not os.path.exists(ACL_FILE): return
        with open(ACL_FILE, 'r', encoding='utf-8') as f: acl = json.load(f)
        targets = set(acl.get("forbidden_all", []))
        for role in acl.get("roles", {}).values(): targets.update(role.get("write_access", []))
        count = _process_lock_paths(targets, True)
        print(f"{GREEN}[완료] {count}개의 구역이 봉인되었습니다.{RESET}", flush=True)
        sys.stdout.flush()
    except Exception as e:
        print(f"{RED}[오류] 봉인 실패: {e}{RESET}", flush=True)
        sys.stdout.flush()

def auto_relock_task():
    """시간 초과 시 자동으로 빗장을 잠그는 콜백"""
    global current_token, permitted_tool
    if running:
        print(f"\n{RED}[보안] 작업 시간 초과(120초)로 인해 성역을 자동으로 재봉인했습니다.{RESET}", flush=True)
        sys.stdout.flush()
        lock_all_sanctuaries()
        current_token = None
        permitted_tool = None

def cleanup():
    """종료 시 정화 및 제어권 반환"""
    global running
    if not running: return
    running = False
    print(f"\n{YELLOW}[SHUTDOWN] 가디언을 종료합니다.{RESET}", flush=True)
    sys.stdout.flush()
    release_all_locks()
    for f in [PORT_FILE, PID_FILE]:
        if os.path.exists(f): 
            try: os.remove(f)
            except: pass
    print(f"\n{MAGENTA}[REPORT] 물리적 봉인 해제 완료. 이제 터미널 제어권을 반환합니다.{RESET}", flush=True)
    sys.stdout.flush()
    time.sleep(1)

def signal_handler(sig, frame):
    cleanup()
    os._exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def get_approval_ui(tool, intent, payload="", target_file=""):
    """내용물 전수 검사 포함 결재 UI (V25.4.2 이중 장벽 보안)"""
    global pending_response, is_waiting_approval
    if not running: return "DENIED"
    
    # [V25.4.2] 확장된 파멸적 키워드 리스트
    p_lower = str(payload).lower()
    nuclear_keywords = ["restore", "reset --hard", "clean", "push -f", "push --force", "branch -d", "rm -rf", "rd /s", "del /s", "remove-item", "format", "wipe", "truncate"]
    is_nuclear = any(k in p_lower for k in nuclear_keywords)
    
    is_self_update = target_file and any(f in target_file for f in ["partner_guard.py", "guardian.py"])
    is_lazy = False if is_self_update else any(k in p_lower for k in ["...", "(상동)", "(중략)", "unchanged", "rest of code"])
    
    # [V25.4.0] 라이트 제한(Write-File Restriction) 및 경로 인식 강화
    is_write_file_violation = False
    debug_path = "N/A"
    if tool == "write_file" and target_file:
        clean_target = target_file.replace('/', os.sep).lstrip(os.sep)
        full_path = os.path.normpath(os.path.join(PROJECT_ROOT, clean_target))
        debug_path = full_path
        if os.path.exists(full_path):
            is_write_file_violation = True

    can_approve = True
    violation_reason = ""
    if is_nuclear:
        can_approve = False
        violation_reason = "파멸적 명령어 감지"
    elif is_lazy:
        can_approve = False
        violation_reason = "지능적 나태함(축약) 감지"
    elif is_write_file_violation:
        can_approve = False
        violation_reason = "기존 파일에 대한 write_file 오용"

    # 브리핑 출력
    print("\n" * 2, flush=True)
    status_msg = f"{YELLOW}파일 수정을 위한 승인이 필요합니다{RESET}" if can_approve else f"{RED}[사법 위반] {violation_reason}{RESET}"
    print(f" [ 작업 브리핑 ] {status_msg}", flush=True)
    print(f"\n {CYAN}도구   :{RESET} {tool}", flush=True)
    print(f" {CYAN}의도   :{RESET} {intent}", flush=True)
    if target_file:
        print(f" {CYAN}대상   :{RESET} {YELLOW}{target_file}{RESET} {GRAY}(검사: {debug_path}){RESET}", flush=True)
    if payload:
        preview = (payload[:150].replace('\n', ' ') + '...') if len(payload) > 150 else payload.replace('\n', ' ')
        print(f" {CYAN}내용물 :{RESET} {WHITE}{preview}{RESET}", flush=True)
    print(f"\n{WHITE} ---------------------------------------------------- {RESET}", flush=True)
    
    if can_approve:
        print(f" {GREEN}[SPACE] 승인{RESET}  |  {RED}[ESC] 거부 및 반려{RESET}", flush=True)
        print(f"{WHITE} ---------------------------------------------------- {RESET}", flush=True)
        sys.stdout.flush()
        is_waiting_approval = True
        input_event.clear()
        is_timed_out = not input_event.wait(timeout=120.0)
        is_waiting_approval = False
        if is_timed_out:
            print(f"\n{RED}[타임아웃] 120초간 응답이 없어 작업을 자동 반려합니다.{RESET}", flush=True)
            pending_response = "DENIED"
        elif pending_response == "APPROVED":
            print(f"\n{GREEN}[결정] 파트너가 승인했습니다. 빗장을 개방합니다...{RESET}", flush=True)
        else:
            print(f"\n{RED}[반려] 파트너 거부로 인해 요청이 기각되었습니다.{RESET}", flush=True)
            pending_response = "DENIED"
    else:
        # [V25.3.8] 즉각 기각
        print(f" {RED}[사법 차단] 위반 사항이 발견되어 요청을 즉시 기각했습니다.{RESET}", flush=True)
        print(f"{WHITE} ---------------------------------------------------- {RESET}", flush=True)
        pending_response = "DENIED"
        
    sys.stdout.flush()
    return pending_response

def keyboard_listener():
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
                elif key == b'\x1b':
                    if is_waiting_approval:
                        pending_response = "DENIED"
                        input_event.set()
                    else: cleanup(); os._exit(0)
        except: pass
        time.sleep(0.1)

def agent_handler(server_socket):
    """프리즘 파트너 요청 처리 (V25.4.2 이중 장벽 보안 체계)"""
    global current_token, permitted_tool, relock_timer
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
                    action = req.get("action")
                    if action == "ASK_APPROVAL":
                        tool = req.get("tool", "Unknown")
                        intent = req.get("intent", "의도 누락")
                        payload = req.get("payload", "")
                        target_file = req.get("target_file") or req.get("file", "")
                        result = get_approval_ui(tool, intent, payload, target_file)
                        if result == "APPROVED":
                            current_token = secrets.token_hex(4).upper()
                            permitted_tool = tool
                            if target_file:
                                full_p = os.path.normpath(os.path.join(PROJECT_ROOT, target_file.replace('/', os.sep).lstrip(os.sep)))
                                set_readonly(full_p, False)
                                print(f"{CYAN}[개방] {target_file}의 빗장을 개방했습니다.{RESET}", flush=True)
                            if relock_timer: relock_timer.cancel()
                            relock_timer = threading.Timer(120.0, auto_relock_task)
                            relock_timer.start()
                            client.send(json.dumps({"status": "APPROVED", "token": current_token}).encode('utf-8'))
                        else: client.send(json.dumps({"status": "DENIED"}).encode('utf-8'))
                    elif action == "VERIFY_TOKEN":
                        token = req.get("token")
                        tool = req.get("tool")
                        payload = req.get("payload", "") # [V25.4.2] 실행 시점 내용물 수령
                        
                        # 내용물 재검사 (파멸적 코드 또는 나태함)
                        p_lower = str(payload).lower()
                        nuclear_keywords = ["restore", "reset --hard", "clean", "push -f", "push --force", "branch -d", "rm -rf", "rd /s", "del /s", "remove-item", "format", "wipe", "truncate"]
                        is_nuclear_exec = any(k in p_lower for k in nuclear_keywords)
                        is_lazy_exec = any(k in p_lower for k in ["...", "(상동)", "(중략)", "unchanged"])
                        
                        if current_token and token == current_token and tool == permitted_tool:
                            if is_nuclear_exec or is_lazy_exec:
                                # [V25.4.2] 실행 시점 기만 적발
                                reason = "파멸적 코드 감지" if is_nuclear_exec else "지능적 나태함 감지"
                                print(f"\n{BG_RED}{WHITE} [경고] 실행 시점 사법 위반 적발! {RESET}", flush=True)
                                print(f" {RED}사유: 실행하려는 내용물에서 {reason}되었습니다.{RESET}", flush=True)
                                print(f" {RED}조치: 해당 작업의 집행권을 즉시 박탈했습니다.{RESET}\n", flush=True)
                                sys.stdout.flush()
                                client.send(json.dumps({"status": "INVALID"}).encode('utf-8'))
                            else:
                                client.send(json.dumps({"status": "VALID"}).encode('utf-8'))
                        else:
                            # [V25.4.1] 도구 바꿔치기 적발
                            print(f"\n{BG_RED}{WHITE} [경고] 사법적 기만 시도 적발! {RESET}", flush=True)
                            print(f" {RED}사유: 승인된 도구({permitted_tool})와 실행 도구({tool})가 일치하지 않습니다.{RESET}", flush=True)
                            print(f" {RED}조치: 해당 도구의 실행 권한을 물리적으로 차단했습니다.{RESET}\n", flush=True)
                            sys.stdout.flush()
                            client.send(json.dumps({"status": "INVALID"}).encode('utf-8'))
                    elif action == "FINISH_WORK":
                        if relock_timer: relock_timer.cancel(); relock_timer = None
                        current_token = None; permitted_tool = None
                        target_file = req.get("target_file") or req.get("file", "")
                        if target_file:
                            full_p = os.path.normpath(os.path.join(PROJECT_ROOT, target_file.replace('/', os.sep).lstrip(os.sep)))
                            set_readonly(full_p, True)
                            print(f"{CYAN}[봉인] {target_file} 재봉인 완료.{RESET}", flush=True)
                        client.send(json.dumps({"status": "OK"}).encode('utf-8'))
                except: break
            if client: client.close()
        except: continue

def main():
    if os.name == 'nt':
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        kernel32.SetConsoleTitleW("PRISM PARTNER GUARD V25.4.2")
    with open(PID_FILE, 'w', encoding='utf-8') as f: f.write(str(os.getpid()))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 0))
    server.listen(1)
    port = server.getsockname()[1]
    with open(PORT_FILE, 'w', encoding='utf-8') as f: f.write(str(port))
    print(f"{MAGENTA}===================================================={RESET}", flush=True)
    print(f"{MAGENTA}    PROJECT FREEISM: PRISM PARTNER GUARD V25.4.2{RESET}", flush=True)
    print(f"{MAGENTA}===================================================={RESET}", flush=True)
    print(f"{CYAN} 상태       : {GREEN}파트너의 주권 수호 중 (가동 중){RESET}", flush=True)
    print(f"{CYAN} 신호 포트   : {port}{RESET}", flush=True)
    print(f"{YELLOW} 알림       : 프리즘 파트너의 작업 신호를 대기 중...{RESET}", flush=True)
    print(f"{MAGENTA}===================================================={RESET}\n", flush=True)
    sys.stdout.flush()
    lock_all_sanctuaries()
    print(f"\n{GREEN}[완료] 모든 구역의 물리적 봉인이 완료되었습니다.{RESET}", flush=True)
    print(f"{CYAN}[대기] 프리즘 파트너(Gemini)의 작업 요청을 기다리는 중입니다...{RESET}\n", flush=True)
    sys.stdout.flush()
    threading.Thread(target=keyboard_listener, daemon=True).start()
    agent_handler(server)

if __name__ == "__main__":
    try: main()
    except Exception as e:
        if running: print(f"{RED}[CRITICAL] Guard Failed: {e}{RESET}", flush=True)
        cleanup()
