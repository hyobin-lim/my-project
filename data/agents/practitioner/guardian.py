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
BG_RED = "\033[41m"

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
PID_FILE = os.path.join(DATA_DIR, 'guardian.pid')
PORT_FILE = os.path.join(DATA_DIR, 'port.txt')
SYNAPSE_FILE = os.path.join(DATA_DIR, 'practitioner_synapse.json')
ACL_FILE = os.path.join(PROJECT_ROOT, 'AI_CORE', 'LOGS', 'practitioner', 'ACL_PRACTITIONER.json')
STRIKE_FILE = os.path.join(PROJECT_ROOT, 'AI_CORE', 'LOGS', 'practitioner', 'STRIKE_LEDGER.jsonl')
PHYSICAL_BLOCK_FILE = os.path.join(PROJECT_ROOT, 'AI_CORE', 'LOGS', 'practitioner', 'PHYSICAL_BLOCK_PRACTITIONER.jsonl')

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
current_authorized_files = {} # [V26.5] 에이전트별 현재 승인된 파일 추적
relock_timers = {} # 에이전트별 자동 봉인 타이머

def get_clean_chars(text):
    """공백과 줄바꿈을 제외한 순수 글자 수 계산"""
    return len("".join(text.split()))

def get_vocabulary_count(text):
    """중복을 제외한 고유 단어 수 계산 (질적 다양성 지표)"""
    return len(set(text.split()))

def get_landmarks(text):
    """핵심 구조물(Header, ARTICLE, const 등) 추출"""
    import re
    pattern = r"(##\s+.+|ARTICLE\s+\d+|\[STAMP\]|const\s+\w+|function\s+\w+|import\s+.+)"
    return set(re.findall(pattern, text))

def set_readonly(path, make_readonly):
    """파일 속성 설정"""
    try:
        mode = os.stat(path).st_mode
        if make_readonly: os.chmod(path, mode & ~stat.S_IWRITE)
        else: os.chmod(path, mode | stat.S_IWRITE)
        return True
    except: return False

def _process_lock_paths(paths, make_readonly):
    """경로 잠금/해제 처리 (호흡권 보장 및 재귀적 스캔)"""
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
            # 실무자용 가디언은 UI 출력량을 조절하여 소음 방지
            if total > 100 and (i + 1) % max(1, total // 10) == 0:
                percent = int(((i + 1) / total) * 100)
                status = "봉인" if make_readonly else "해방"
                print(f"\r{CYAN}[{status}] {percent}% 완료 ({i + 1}/{total})...{RESET}", end="", flush=True)
        except: continue
            
    if total > 100: print() # 진행률 표시 후 줄바꿈
    return processed_count

def apply_global_protection(protect=True):
    """ACL 구역 정밀 성역화 (호흡권 보장형)"""
    status = "봉인" if protect else "해제"
    print(f"\n{CYAN}[{status}] ACL 기반 정밀 성역화 집행 중...{RESET}", flush=True)
    sys.stdout.flush()
    try:
        if not os.path.exists(ACL_FILE): return
        with open(ACL_FILE, 'r', encoding='utf-8') as f: acl = json.load(f)
        targets = set(acl.get("forbidden_all", []))
        for role in acl.get("roles", {}).values(): targets.update(role.get("write_access", []))
        count = _process_lock_paths(targets, protect)
        print(f"{GREEN}[완료] {count}개의 핵심 자산이 {status}되었습니다.{RESET}", flush=True)
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

def record_physical_block(tool, target_file, violation_type, reason):
    """물리적 진압 기록 (V28.9+)"""
    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tool": tool,
        "target": target_file,
        "violation_type": violation_type,
        "reason": reason,
    }
    try:
        if os.path.exists(PHYSICAL_BLOCK_FILE):
            set_readonly(PHYSICAL_BLOCK_FILE, False)
        with open(PHYSICAL_BLOCK_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        set_readonly(PHYSICAL_BLOCK_FILE, True)
    except:
        pass

class SynapseHandler(FileSystemEventHandler):
    """비대면 신호 파일 감시 및 자동 결재 연동 (V30.0)"""
    def on_created(self, event): self.process_synapse(event)
    def on_modified(self, event): self.process_synapse(event)

    def process_synapse(self, event):
        global pending_response, current_tokens, current_authorized_files, relock_timers
        if event.is_directory or not event.src_path.endswith("practitioner_synapse.json"):
            return

        try:
            time.sleep(0.1)
            with open(SYNAPSE_FILE, "r", encoding="utf-8") as f:
                req = json.load(f)

            action = req.get("action")
            role = req.get("role", "UNKNOWN")
            
            if action == "ASK_APPROVAL":
                target_file = req.get("target_file") or req.get("file", "")
                result = get_approval_ui(role, req.get("tool"), target_file, req.get("payload", ""))

                response_status = "DENIED"
                token = None

                if result == "APPROVED":
                    response_status = "APPROVED"
                    token = secrets.token_hex(4).upper()
                    current_tokens[role] = {"token": token, "tool": req.get("tool")}
                    current_authorized_files[role] = {"file": target_file, "tool": req.get("tool")}
                    
                    full_p = os.path.normpath(os.path.join(PROJECT_ROOT, target_file.replace("/", os.sep).lstrip(os.sep)))
                    set_readonly(full_p, False)
                    pending_unlocks.add(full_p)

                    if role in relock_timers: relock_timers[role].cancel()
                    relock_timers[role] = threading.Timer(120.0, auto_relock_task, args=[role])
                    relock_timers[role].start()

                resp_file = SYNAPSE_FILE.replace(".json", "_response.json")
                with open(resp_file, "w", encoding="utf-8") as f:
                    json.dump({"status": response_status, "token": token}, f)

            elif action == "FINISH_WORK":
                target_file = req.get("target_file") or req.get("file", "")
                if target_file:
                    full_p = os.path.normpath(os.path.join(PROJECT_ROOT, target_file.replace("/", os.sep).lstrip(os.sep)))
                    set_readonly(full_p, True)
                
                if role in relock_timers:
                    relock_timers[role].cancel()
                    del relock_timers[role]
                if role in current_tokens: del current_tokens[role]
                if role in current_authorized_files: del current_authorized_files[role]

                resp_file = SYNAPSE_FILE.replace(".json", "_response.json")
                with open(resp_file, "w", encoding="utf-8") as f:
                    json.dump({"status": "OK"}, f)

            if os.path.exists(SYNAPSE_FILE):
                os.remove(SYNAPSE_FILE)
        except Exception as e:
            print(f"{RED}[오류] 비대면 신호 처리 실패: {e}{RESET}")

def synapse_interceptor_thread():
    """실무자 도구 무단 호출 정밀 감시 (V28.9 GAIA IRON-FIST)"""
    global current_tokens, running
    while running:
        try:
            if os.name == "nt":
                cmd = "wmic process where \"name='python.exe'\" get commandline,processid"
                output = subprocess.check_output(cmd, shell=True).decode("utf-8", errors="ignore")
                for line in output.splitlines():
                    tools = ["replace.py", "write_file.py", "run_shell_command.py", "delete_file.py"]
                    for t_file in tools:
                        if t_file in line:
                            t_name = t_file.replace(".py", "")
                            # 모든 활성 토큰 중 해당 도구와 일치하는 것이 있는지 확인
                            authorized = False
                            for role, data in current_tokens.items():
                                if data.get("tool") == t_name:
                                    authorized = True
                                    break
                            
                            if not authorized:
                                parts = line.split()
                                if not parts: continue
                                pid = parts[-1]
                                if pid.isdigit():
                                    subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
                                    print(f"\n{BG_RED}{WHITE} [물리적 진압] 실무자 무단 도구 호출 즉각 사살: {t_name} (PID: {pid}) {RESET}")
                                    record_physical_block(t_name, "UNKNOWN", "TOOL_ASSET_LOCKED", "실무자 무단 도구 호출")
            time.sleep(0.01)
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
    """실무자용 내용물 전수 검사 결재 UI (V29.0 SENTINEL 이식)"""
    global pending_response, is_waiting_approval, current_authorized_files, current_tokens
    if not running: return "DENIED"
    
    # [V26.5] 세션 효율성 훅 체크
    is_auto_pass = False
    stored_session = current_authorized_files.get(role, {})
    if file_path and file_path == stored_session.get("file") and tool == stored_session.get("tool"):
        is_auto_pass = True

    p_lower = str(payload).lower()
    nuclear_keywords = ["restore", "reset --hard", "clean", "push -f", "push --force", "branch -d", "rm -rf", "rd /s", "del /s", "remove-item", "format", "wipe", "truncate"]
    is_nuclear = any(k in p_lower for k in nuclear_keywords)
    
    is_self_update = file_path and any(f in file_path for f in ["partner_guard.py", "guardian.py"])
    
    lazy_keywords = ["...", "(상동)", "(중략)", "(생략)", "unchanged", "rest of code", "기존 코드 유지", "동일함", "생략함"]
    is_lazy = False if is_self_update else any(k in p_lower for k in lazy_keywords)
    
    if tool == "write_file": is_auto_pass = False

    can_approve = True
    is_warning_mode = False # V29.0 SENTINEL
    violation_reason = ""

    # [V26.0] 지능형 밀도 분석
    density_report = ""
    char_ratio = 100.0
    
    if payload and tool in ["replace", "write_file"]:
        clean_target = file_path.replace('/', os.sep).lstrip(os.sep)
        full_path = os.path.normpath(os.path.join(PROJECT_ROOT, clean_target))
        
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                    old_content = f.read()
                old_chars = get_clean_chars(old_content)
                new_chars = get_clean_chars(str(payload))
                char_ratio = (new_chars / old_chars * 100) if old_chars > 0 else 100
                density_report = f"[감찰] 정보보존율: {char_ratio:.1f}%"
            except: pass

    # 원칙 적용
    if char_ratio < 30.0: # 데이터 학살 (Purity Guard)
        can_approve = False
        violation_reason = f"데이터 학살 감지 (보존율 {char_ratio:.1f}%)"
    elif is_nuclear:
        if tool == "run_shell_command": # 실제 실행은 즉각 차단
            can_approve = False
            violation_reason = "파멸적 명령어 실행 시도 (차단)"
        else: # 기록용은 경고 후 파트너 결정
            is_warning_mode = True
            violation_reason = "⚠️ [주의] 파멸적 단어 포함됨 (기록용인지 확인 필요)"
    elif is_lazy:
        can_approve = False
        violation_reason = "지능적 나태함(축약) 감지"

    if is_auto_pass and can_approve and not is_warning_mode:
        return "APPROVED"

    print("\n" * 2, flush=True)
    
    if is_warning_mode:
        status_msg = f"{BG_RED}{WHITE} [심각] 파멸적 단어 감지: {violation_reason} {RESET}"
    else:
        status_msg = f"{YELLOW}{role}의 작업 승인이 필요합니다{RESET}" if can_approve else f"{RED}[사법 위반] {violation_reason}{RESET}"
    
    print(f" [ 실무자 요청 ] {status_msg}", flush=True)
    if density_report: print(f" {CYAN}{density_report}{RESET}", flush=True)

    print(f"\n {CYAN}에이전트 :{RESET} {role}")
    print(f" {CYAN}도구     :{RESET} {tool}")
    print(f" {CYAN}대상     :{RESET} {YELLOW}{file_path}{RESET}")
    
    if payload:
        preview = (str(payload)[:150].replace('\n', ' ') + '...') if len(str(payload)) > 150 else str(payload).replace('\n', ' ')
        print(f" {CYAN}내용물   :{RESET} {WHITE}{preview}{RESET}")
        
    print(f"\n{WHITE} ---------------------------------------------------- {RESET}", flush=True)
    if can_approve:
        print(f" {GREEN}[SPACE] 승인{RESET}  |  {RED}[ESC] 거부 및 반려{RESET}", flush=True)
    else:
        print(f" {RED}[!] 위반 사항 적발로 승인 불가. [ESC]로 즉시 반려하십시오.{RESET}", flush=True)
    print(f"{WHITE} ---------------------------------------------------- {RESET}", flush=True)
    sys.stdout.flush()

    is_waiting_approval = True
    input_event.clear()
    is_timed_out = not input_event.wait(timeout=120.0)
    is_waiting_approval = False
    
    if is_timed_out:
        print(f"\n{RED}[타임아웃] 자동 반려{RESET}", flush=True)
        pending_response = "DENIED"
    elif pending_response == "APPROVED":
        print(f"\n{GREEN}[결정] 파트너 승인 완료{RESET}", flush=True)
    else:
        print(f"\n{RED}[결정] 파트너 반려{RESET}", flush=True)
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
                            current_authorized_files[role] = {"file": req.get("file"), "tool": req.get("tool")} # [V26.5] 세션 기록
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
                        if role in current_authorized_files: del current_authorized_files[role] # [V26.5] 세션 초기화
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
        kernel32.SetConsoleTitleW("PRISM JUDGE V26.0 (GAIA EDITION)")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 0))
    server.listen(10)
    with open(PORT_FILE, 'w', encoding='utf-8') as f: f.write(str(server.getsockname()[1]))
    with open(PID_FILE, 'w', encoding='utf-8') as f: f.write(str(os.getpid()))
    
    print(f"{CYAN}===================================================={RESET}", flush=True)
    print(f"{CYAN}    PROJECT FREEISM: PRISM JUDGE V26.0 GAIA{RESET}", flush=True)
    print(f"{CYAN}===================================================={RESET}", flush=True)
    sys.stdout.flush()
    apply_global_protection(True)
    print(f"\n{GREEN}[완료] 실무자 구역의 물리적 방화벽이 가동되었습니다.{RESET}", flush=True)
    print(f"{CYAN}[감시] 실무자 AI(T1, T2)의 작업 신호를 대기 중...{RESET}\n", flush=True)
    sys.stdout.flush()
    
    threading.Thread(target=agent_listener, args=(server,), daemon=True).start()
    threading.Thread(target=keyboard_monitor, args=(), daemon=True).start()
    threading.Thread(target=synapse_interceptor_thread, args=(), daemon=True).start()

    observer = Observer()
    observer.schedule(SanctuaryHandler(), PROJECT_ROOT, recursive=True)
    observer.schedule(SynapseHandler(), DATA_DIR, recursive=False)
    observer.start()
    print(f"{CYAN}[알림] 비대면 신호(practitioner_synapse.json) 감시 가동 중...{RESET}", flush=True)

    try:
        while running: time.sleep(1)

    finally: cleanup(); observer.stop(); observer.join()

if __name__ == "__main__":
    try: main()
    except Exception as e:
        if running: print(f"{RED}[CRITICAL] Judge Failed: {e}{RESET}", flush=True)
        cleanup()
