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

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PRISM_HOME = os.path.dirname(os.path.abspath(__file__))
PORT_FILE = os.path.join(PRISM_HOME, "partner_port.txt")
PID_FILE = os.path.join(PRISM_HOME, "partner_guard.pid")
SYNAPSE_FILE = os.path.join(PRISM_HOME, "partner_synapse.json")
ACL_FILE = os.path.join(PROJECT_ROOT, "AI_CORE", "LOGS", "prism_partner", "ACL_PARTNER.json")
PHYSICAL_BLOCK_FILE = os.path.join(
    PROJECT_ROOT, "AI_CORE", "LOGS", "prism_partner", "PHYSICAL_BLOCK.jsonl"
)

# 전역 상태
pending_response = None
input_event = threading.Event()
is_waiting_approval = False
running = True
current_token = None
permitted_tool = None
is_token_verified = False  # 토큰 검증 여부 (V28.9+ 부활)
current_authorized_file = None
open_sanctuaries = set()  # 현재 개방된 성역 목록 (V28.8)
last_approval_type = None  # 최근 승인 사유 (V28.9+)
cached_landmarks = None
relock_timer = None
current_port = 0


class SynapseHandler(FileSystemEventHandler):
    """비대면 신호 파일 감시 및 자동 결재 연동 (V30.0)"""

    def on_created(self, event):
        self.process_synapse(event)

    def on_modified(self, event):
        self.process_synapse(event)

    def process_synapse(self, event):
        global pending_response, current_token, permitted_tool, current_authorized_file, open_sanctuaries, relock_timer, is_token_verified
        if event.is_directory or not event.src_path.endswith("partner_synapse.json"):
            return

        try:
            # 파일이 완전히 쓰여질 때까지 잠시 대기
            time.sleep(0.1)
            with open(SYNAPSE_FILE, "r", encoding="utf-8") as f:
                req = json.load(f)

            action = req.get("action")
            if action == "ASK_APPROVAL":
                # 수술적 정밀도: 기존 성역 봉인
                if open_sanctuaries:
                    for old_f in list(open_sanctuaries):
                        full_p = os.path.normpath(
                            os.path.join(
                                PROJECT_ROOT, old_f.replace("/", os.sep).lstrip(os.sep)
                            )
                        )
                        set_readonly(full_p, True)
                    open_sanctuaries.clear()

                is_token_verified = False
                target_file = req.get("target_file") or req.get("file", "")
                result = get_approval_ui(
                    req.get("tool"),
                    req.get("intent"),
                    req.get("payload", ""),
                    target_file,
                )

                response_status = "DENIED"
                token = None

                if result == "APPROVED":
                    response_status = "APPROVED"
                    token = secrets.token_hex(4).upper()
                    current_token = token
                    permitted_tool = req.get("tool")
                    current_authorized_file = target_file
                    if current_authorized_file:
                        open_sanctuaries.add(current_authorized_file)
                        full_p = os.path.normpath(
                            os.path.join(
                                PROJECT_ROOT,
                                current_authorized_file.replace("/", os.sep).lstrip(
                                    os.sep
                                ),
                            )
                        )
                        set_readonly(full_p, False)

                    if relock_timer:
                        relock_timer.cancel()
                    relock_timer = threading.Timer(300.0, auto_relock_task)
                    relock_timer.start()
                    print_status_footer()

                # 결과 파일 생성 (비대면 응답)
                resp_file = SYNAPSE_FILE.replace(".json", "_response.json")
                with open(resp_file, "w", encoding="utf-8") as f:
                    json.dump({"status": response_status, "token": token}, f)

            elif action == "VERIFY_TOKEN":
                status = "INVALID"
                if (
                    current_token
                    and req.get("token") == current_token
                    and req.get("tool") == permitted_tool
                ):
                    is_token_verified = True
                    status = "VALID"
                    print_status_footer()

                resp_file = SYNAPSE_FILE.replace(".json", "_response.json")
                with open(resp_file, "w", encoding="utf-8") as f:
                    json.dump({"status": status}, f)

            elif action == "FINISH_WORK":
                target_file = req.get("target_file") or req.get("file", "")
                if target_file and target_file in open_sanctuaries:
                    open_sanctuaries.remove(target_file)
                    full_p = os.path.normpath(
                        os.path.join(
                            PROJECT_ROOT,
                            target_file.replace("/", os.sep).lstrip(os.sep),
                        )
                    )
                    set_readonly(full_p, True)

                if relock_timer:
                    relock_timer.cancel()
                    relock_timer = None
                current_token = None
                permitted_tool = None
                if target_file == current_authorized_file:
                    current_authorized_file = None
                print_status_footer()

                resp_file = SYNAPSE_FILE.replace(".json", "_response.json")
                with open(resp_file, "w", encoding="utf-8") as f:
                    json.dump({"status": "OK"}, f)

            # 처리가 끝나면 신호 파일 삭제
            if os.path.exists(SYNAPSE_FILE):
                os.remove(SYNAPSE_FILE)

        except Exception as e:
            print(f"{RED}[오류] 비대면 신호 처리 실패: {e}{RESET}")


def print_status_footer():
    """이중 계층 감시 인터페이스 (V28.9 GAIA IRON-FIST)"""
    # 1층: 도구 상태
    if permitted_tool:
        tool_info = f"{GREEN}ACTIVE: {permitted_tool}{RESET} {GRAY}(그 외 모든 도구 사살 중){RESET}"
    else:
        tool_info = f"{RED}LOCKED: 모두 차단{RESET} {GRAY}(사법 승인 대기 중){RESET}"

    # 2층: 성역(파일) 상태
    if open_sanctuaries:
        file_list = ", ".join([f"{YELLOW}{f}{RESET}" for f in open_sanctuaries])
        file_info = f"{CYAN}OPEN: {file_list}{RESET}"
    else:
        file_info = f"{RED}CLOSED: 모두 봉인{RESET} {GRAY}(물리적 잠금 유지){RESET}"

    # 3층: 허용 사유 (V28.9+ 추가)
    reason_info = (
        f"{WHITE}{last_approval_type}{RESET}"
        if last_approval_type
        else f"{GRAY}사법적 대기 상태{RESET}"
    )

    sys.stdout.write(f"\n{MAGENTA}[GAIA MONITOR]{RESET}\n")
    sys.stdout.write(f" 🛠 도구 > {tool_info}\n")
    sys.stdout.write(f" 📂 파일 > {file_info}\n")
    sys.stdout.write(f" 💡 사유 > {reason_info}\n")
    sys.stdout.flush()


def rotate_logs(file_path, max_kb=50):
    try:
        if not os.path.exists(file_path):
            return
        file_size = os.path.getsize(file_path) / 1024
        if file_size > max_kb:
            # 로그 정화 시 잠시 쓰기 권한 부여
            set_readonly(file_path, False)
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            keep_lines = lines[len(lines) // 2 :]
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(keep_lines)
            set_readonly(file_path, True)
            print(
                f"{YELLOW}[장부 정화] 용량 {int(file_size)}KB 도달로 하위 50% 기록을 절단했습니다.{RESET}"
            )
    except:
        pass


def record_physical_block(tool, target_file, violation_type, reason):
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
        rotate_logs(PHYSICAL_BLOCK_FILE)
    except:
        pass


def get_clean_chars(text):
    return len("".join(text.split()))


def get_vocabulary_count(text):
    return len(set(text.split()))


def get_landmarks(text):
    import re

    pattern = (
        r"(##\s+.+|ARTICLE\s+\d+|\[STAMP\]|const\s+\w+|function\s+\w+|import\s+.+)"
    )
    return set(re.findall(pattern, text))


def set_readonly(path, make_readonly):
    try:
        if not os.path.exists(path):
            return False
        mode = os.stat(path).st_mode
        if make_readonly:
            os.chmod(path, mode & ~stat.S_IWRITE)
        else:
            os.chmod(path, mode | stat.S_IWRITE)
        return True
    except:
        return False


def _process_lock_paths(paths, make_readonly):
    processed_count = 0
    heavy_dirs = set(
        [
            "node_modules",
            ".git",
            ".venv",
            "__pycache__",
            "dist",
            "build",
            ".next",
            "out",
            "backup",
            "backups",
        ]
    )
    breathing_exts = (".txt", ".pid", ".log")

    all_files = []
    for target in paths:
        clean_target = target.strip().replace("/", os.sep).lstrip(os.sep)
        full_p = os.path.normpath(os.path.join(PROJECT_ROOT, clean_target))
        if os.path.isdir(full_p):
            for root, dirs, files in os.walk(full_p, topdown=True):
                dirs[:] = [d for d in dirs if d not in heavy_dirs]
                for file in files:
                    if not file.lower().endswith(breathing_exts):
                        all_files.append(os.path.join(root, file))
        elif os.path.exists(full_p):
            if not full_p.lower().endswith(breathing_exts):
                all_files.append(full_p)

    total = len(all_files)
    if total == 0:
        return 0

    status_word = "봉인" if make_readonly else "해방"
    for i, file_path in enumerate(all_files):
        if set_readonly(file_path, make_readonly):
            processed_count += 1
        if total > 5:
            percent = int(((i + 1) / total) * 100)
            print(
                f"\r{CYAN}[{status_word}] {percent}% 완료 ({i + 1}/{total})...{RESET}",
                end="",
                flush=True,
            )

    if total > 5:
        print(
            f"\n{GREEN}✔ [물리적 {status_word} 확정] 총 {processed_count}개 파일 처리 완료.{RESET}"
        )
    return processed_count


def lock_all_sanctuaries():
    """핵심 자산 물리적 봉인"""
    try:
        if not os.path.exists(ACL_FILE):
            return
        with open(ACL_FILE, "r", encoding="utf-8") as f:
            acl = json.load(f)
        targets = set(acl.get("forbidden_all", []))
        for role in acl.get("roles", {}).values():
            targets.update(role.get("write_access", []))
        _process_lock_paths(targets, True)
    except:
        pass
    print_status_footer()


def auto_relock_task():
    """300초 타임아웃 일괄 강제 재봉인 (V28.9)"""
    global current_token, permitted_tool, current_authorized_file, open_sanctuaries
    if running:
        if open_sanctuaries:
            locked_list = list(open_sanctuaries)
            for f_path in locked_list:
                full_p = os.path.normpath(
                    os.path.join(
                        PROJECT_ROOT, f_path.replace("/", os.sep).lstrip(os.sep)
                    )
                )
                set_readonly(full_p, True)
            print(
                f"\n{RED}[타임아웃] 300초 경과 - {len(locked_list)}개 성역 일괄 강제 재봉인 완료{RESET}"
            )
            print(f"{GRAY} 대상: {', '.join(locked_list)}{RESET}")

        current_token = None
        permitted_tool = None
        current_authorized_file = None
        open_sanctuaries.clear()
        print_status_footer()


def synapse_interceptor_thread():
    """도구 전용 정밀 감시 (V28.9 GAIA IRON-FIST)"""
    global current_token, permitted_tool, is_token_verified, running
    while running:
        try:
            if os.name == "nt":
                cmd = (
                    "wmic process where \"name='python.exe'\" get commandline,processid"
                )
                output = subprocess.check_output(cmd, shell=True).decode(
                    "utf-8", errors="ignore"
                )
                for line in output.splitlines():
                    tools = [
                        "replace.py",
                        "write_file.py",
                        "run_shell_command.py",
                        "delete_file.py",
                        "rename_file.py",
                        "move_file.py",
                    ]
                    for t_file in tools:
                        if t_file in line:
                            t_name = t_file.replace(".py", "")
                            # 토큰이 없거나, 도구가 다르거나, 토큰 검증이 완료되지 않은 경우 즉각 사살
                            if (
                                not current_token
                                or t_name != permitted_tool
                                or not is_token_verified
                            ):
                                parts = line.split()
                                if not parts:
                                    continue
                                pid = parts[-1]
                                if pid.isdigit():
                                    subprocess.run(
                                        f"taskkill /F /PID {pid}",
                                        shell=True,
                                        capture_output=True,
                                    )
                                    print(
                                        f"\n{BG_RED}{WHITE} [물리적 진압] 무단 도구 호출 즉각 사살: {t_name} (PID: {pid}) {RESET}"
                                    )
                                    if not is_token_verified:
                                        print(
                                            f"{YELLOW} 사유: 해당 도구의 토큰 검증(VERIFY_TOKEN)이 완료되지 않았습니다. {RESET}"
                                        )
                                    else:
                                        print(
                                            f"{YELLOW} 사유: 해당 도구 자산이 현재 'LOCKED' 상태입니다. 파트너의 결재를 통해 도구를 'ACTIVE'로 전환하십시오.{RESET}"
                                        )
                                    record_physical_block(
                                        "SYNAPSE",
                                        t_name,
                                        "TOOL_ASSET_LOCKED",
                                        f"도구 자산 무단 사용 시도 (검증 미비)",
                                    )
                                    print_status_footer()
            time.sleep(0.01)
        except:
            pass


def get_approval_ui(tool, intent, payload="", target_file=""):
    """내용물 전수 검사 포함 결재 UI (V25.4.2 스타일 이식)"""
    global pending_response, is_waiting_approval, current_authorized_file, permitted_tool, cached_landmarks, last_approval_type
    if not running:
        return "DENIED"

    # 사유 필드 실시간 동기화
    last_approval_type = intent
    
    is_auto_pass = (
        target_file and target_file in open_sanctuaries and tool == permitted_tool
    )

    p_lower = str(payload).lower()
    nuclear_keywords = [
        "restore",
        "reset --hard",
        "clean",
        "rm -rf",
        "rd /s",
        "del /s",
        "remove-item",
        "format",
        "wipe",
        "truncate",
    ]
    is_nuclear = any(k in p_lower for k in nuclear_keywords)
    is_lazy = any(
        k in p_lower for k in ["...", "(상동)", "(중략)", "unchanged", "rest of code"]
    )

    is_write_file_on_existing = False
    is_exception_applied = False
    debug_path = "N/A"
    if tool == "write_file" and target_file:
        full_path = os.path.normpath(
            os.path.join(PROJECT_ROOT, target_file.replace("/", os.sep).lstrip(os.sep))
        )
        debug_path = full_path
        if os.path.exists(full_path):
            is_write_file_on_existing = True
            valid_exceptions = [
                "신규",
                "리모델링",
                "기술적 한계",
                "이관",
                "통합",
                "임계점",
            ]
            if any(k.lower() in intent.lower() for k in valid_exceptions):
                is_exception_applied = True

    can_approve = True
    is_warning_mode = False  # V29.0: 이중 경고 모드
    violation_reason = ""
    
    # 데이터 순도 가드 (Purity Guard): 보존율 30% 미만은 예외 없이 학살로 간주
    if payload and tool in ["replace", "write_file"] and 'char_ratio' in locals():
        if char_ratio < 30.0:
            can_approve = False
            violation_reason = f"데이터 학살 감지 (보존율 {char_ratio:.1f}%)"

    if not can_approve:
        pass # 이미 학살 판정됨
    elif is_nuclear:
        # V29.0: 실행형 도구(shell)는 즉각 차단, 기록형 도구(replace/write)는 경고 후 파트너 결정
        if tool == "run_shell_command":
            can_approve = False
            violation_reason = "파멸적 명령어 실행 시도 (차단)"
        else:
            is_warning_mode = True
            violation_reason = "⚠️ [주의] 파멸적 단어 포함됨 (기록용인지 확인 필요)"
    elif is_lazy:
        can_approve = False
        violation_reason = "지능적 나태함 (차단)"
    elif is_write_file_on_existing and not is_exception_applied:
        can_approve = False
        violation_reason = "라이트 예외 미달 (차단)"

    if is_auto_pass and can_approve and not is_warning_mode:
        last_approval_type = "연속 작업 세션 보존 (동일 도구 및 파일)"
        return "APPROVED"

    density_report = ""
    if payload and tool in ["replace", "write_file"]:
        clean_target = target_file.replace("/", os.sep).lstrip(os.sep)
        full_path = os.path.normpath(os.path.join(PROJECT_ROOT, clean_target))
        if os.path.exists(full_path):
            try:
                with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                    old_content = f.read()
                if not cached_landmarks:
                    cached_landmarks = get_landmarks(old_content)
                old_chars = get_clean_chars(old_content)
                new_chars = get_clean_chars(str(payload))
                old_vocal = get_vocabulary_count(old_content)
                new_vocal = get_vocabulary_count(str(payload))
                char_ratio = (new_chars / old_chars * 100) if old_chars > 0 else 100
                vocal_ratio = (new_vocal / old_vocal * 100) if old_vocal > 0 else 100
                new_marks = get_landmarks(str(payload))
                lost_marks = cached_landmarks - new_marks
                density_report = (
                    f"[감찰] 정보:{char_ratio:.1f}% | 어휘:{vocal_ratio:.1f}%"
                )
                if lost_marks:
                    density_report += f" | {RED}구조소실:{len(lost_marks)}{RESET}"
            except:
                pass

    print("\n" * 2, flush=True)
    
    # V29.0 시각적 경고 UI
    if is_warning_mode:
        status_msg = f"{BG_RED}{WHITE} [심각] 파멸적 단어 감지: {violation_reason} {RESET}"
        # 시스템 핵심 파일 확인
        core_files = ["partner_guard.py", "ACL_PARTNER.json", ".bat", ".ps1"]
        if any(cf in target_file for cf in core_files):
            status_msg += f"\n {BG_RED}{WHITE} 🚨 [위험] 시스템 핵심 파일 수정 중! 승인 시 마비 위험이 있습니다. {RESET}"
    else:
        status_msg = (
            f"{YELLOW}작업 승인이 필요합니다{RESET}"
            if can_approve
            else f"{RED}[사법 위반] {violation_reason}{RESET}"
        )
    
    print(f" [ 작업 브리핑 ] {status_msg}", flush=True)
    print(f"\n {CYAN}도구   :{RESET} {tool}", flush=True)
    print(f" {CYAN}의도   :{RESET} {intent}", flush=True)
    if target_file:
        print(
            f" {CYAN}대상   :{RESET} {YELLOW}{target_file}{RESET} {GRAY}(검사: {debug_path}){RESET}",
            flush=True,
        )
    if payload:
        preview = (
            (str(payload)[:150].replace("\n", " ") + "...")
            if len(str(payload)) > 150
            else str(payload).replace("\n", " ")
        )
        print(f" {CYAN}내용물 :{RESET} {WHITE}{preview}{RESET}", flush=True)
    if density_report:
        print(f" {CYAN}분석   :{RESET} {density_report}", flush=True)
    print(
        f"\n{WHITE} ---------------------------------------------------- {RESET}",
        flush=True,
    )

    if can_approve:
        print(f" {GREEN}[SPACE] 승인{RESET}  |  {RED}[ESC] 반려{RESET}", flush=True)
        print(
            f"{WHITE} ---------------------------------------------------- {RESET}",
            flush=True,
        )
        is_waiting_approval = True
        input_event.clear()
        is_timed_out = not input_event.wait(timeout=300.0)
        is_waiting_approval = False
        if is_timed_out:
            print(f"\n{RED}[결정] 타임아웃 반려{RESET}")
            record_physical_block(tool, target_file, "TIMEOUT", "무응답")
            pending_response = "DENIED"
            print_status_footer()
        elif pending_response == "APPROVED":
            print(f"\n{GREEN}[결정] 파트너 승인 완료 (빗장 개방){RESET}")
        else:
            print(f"\n{RED}[결정] 파트너 반려{RESET}")
            record_physical_block(tool, target_file, "MANUAL_DENIAL", "거부")
            pending_response = "DENIED"
            print_status_footer()
    else:
        record_physical_block(tool, target_file, "AUTO_REJECT", violation_reason)
        print(f"\n{RED}[결정] 원칙적 즉각 기각{RESET}")
        print(
            f"{WHITE} ---------------------------------------------------- {RESET}",
            flush=True,
        )
        pending_response = "DENIED"
        print_status_footer()
    return pending_response


def keyboard_listener():
    global pending_response, running, is_waiting_approval
    import msvcrt

    while running:
        try:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b" ":
                    if is_waiting_approval:
                        pending_response = "APPROVED"
                        input_event.set()
                elif key == b"\x1b":
                    if is_waiting_approval:
                        pending_response = "DENIED"
                        input_event.set()
                    else:
                        cleanup()
                        os._exit(0)
        except:
            pass
        time.sleep(0.1)


def agent_handler(server_socket):
    global current_token, permitted_tool, relock_timer, current_authorized_file, open_sanctuaries, cached_landmarks
    server_socket.settimeout(1.0)
    decoder = json.JSONDecoder()
    while running:
        client = None
        try:
            client, addr = server_socket.accept()
            raw_data = client.recv(32768).decode("utf-8", errors="replace")
            if not raw_data:
                continue
            buffer = raw_data.strip()
            while buffer:
                try:
                    req, index = decoder.raw_decode(buffer)
                    buffer = buffer[index:].strip()
                    action = req.get("action")
                    if action == "ASK_APPROVAL":
                        # [V28.9 FINAL] 진정한 수술적 정밀도: 새로운 요청 시 기존 성역 일괄 자동 봉인
                        if open_sanctuaries:
                            for old_f in list(open_sanctuaries):
                                full_p = os.path.normpath(os.path.join(PROJECT_ROOT, old_f.replace('/', os.sep).lstrip(os.sep)))
                                set_readonly(full_p, True)
                            print(f"{YELLOW}[자동 봉인] 새로운 요청으로 인해 기존 {len(open_sanctuaries)}개 성역을 일괄 봉인했습니다.{RESET}")
                            open_sanctuaries.clear()
                        
                        is_token_verified = False # 보안 리셋
                        
                        target_file = req.get("target_file") or req.get("file", "")
                        if target_file != current_authorized_file:
                            cached_landmarks = None
                        result = get_approval_ui(
                            req.get("tool"),
                            req.get("intent"),
                            req.get("payload", ""),
                            target_file,
                        )
                        if result == "APPROVED":
                            current_token = secrets.token_hex(4).upper()
                            permitted_tool = req.get("tool")
                            current_authorized_file = target_file
                            if current_authorized_file:
                                open_sanctuaries.add(current_authorized_file)
                                full_p = os.path.normpath(
                                    os.path.join(
                                        PROJECT_ROOT,
                                        current_authorized_file.replace(
                                            "/", os.sep
                                        ).lstrip(os.sep),
                                    )
                                )
                                set_readonly(full_p, False)
                                print(
                                    f"{CYAN}[개방] {current_authorized_file}의 빗장을 개방했습니다.{RESET}"
                                )
                            if relock_timer:
                                relock_timer.cancel()
                            relock_timer = threading.Timer(300.0, auto_relock_task)
                            relock_timer.start()
                            print_status_footer()
                            client.send(
                                json.dumps(
                                    {"status": "APPROVED", "token": current_token}
                                ).encode("utf-8")
                            )
                        else:
                            client.send(
                                json.dumps(
                                    {
                                        "status": "DENIED",
                                        "instruction": "장부 확인 및 교정 필요",
                                    }
                                ).encode("utf-8")
                            )
                    elif action == "VERIFY_TOKEN":
                        if (
                            current_token
                            and req.get("token") == current_token
                            and req.get("tool") == permitted_tool
                        ):
                            is_token_verified = True
                            last_approval_type = f"{permitted_tool} 실행 권한 활성화 (작업 중)"
                            print(
                                f"\n{GREEN}✔ [검증] 토큰 일치: {permitted_tool} 실행 권한이 물리적으로 활성화되었습니다.{RESET}"
                            )
                            print_status_footer()
                            client.send(json.dumps({"status": "VALID"}).encode("utf-8"))
                        else:
                            print(
                                f"\n{BG_RED}{WHITE} [차단] 위조된 토큰 또는 승인되지 않은 도구 접근! ({req.get('tool')}) {RESET}"
                            )
                            record_physical_block(
                                "VERIFY",
                                req.get("tool"),
                                "INVALID_TOKEN",
                                "위조 토큰 사용 시도",
                            )
                            client.send(
                                json.dumps({"status": "INVALID"}).encode("utf-8")
                            )
                    elif action == "FINISH_WORK":
                        target_file = req.get("target_file") or req.get("file", "")
                        if target_file:
                            if target_file in open_sanctuaries:
                                open_sanctuaries.remove(target_file)
                            full_p = os.path.normpath(
                                os.path.join(
                                    PROJECT_ROOT,
                                    target_file.replace("/", os.sep).lstrip(os.sep),
                                )
                            )
                            set_readonly(full_p, True)
                            print(f"{CYAN}[봉인] {target_file} 재봉인 완료.{RESET}")

                        # 물리 작업 완료 후 변수 초기화 및 UI 갱신
                        if relock_timer:
                            relock_timer.cancel()
                            relock_timer = None
                        current_token = None
                        permitted_tool = None
                        last_approval_type = None
                        if target_file == current_authorized_file:
                            current_authorized_file = None
                        print_status_footer()
                        client.send(json.dumps({"status": "OK"}).encode("utf-8"))
                    else:
                        client.send(json.dumps({"status": "ERROR"}).encode("utf-8"))
                except:
                    break
        except:
            continue
        finally:
            if client:
                client.close()


def main():
    global current_port
    if os.name == "nt":
        import ctypes

        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        kernel32.SetConsoleTitleW("PARTNER GUARD V28.9 (GAIA IRON-FIST)")
    with open(PID_FILE, "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    current_port = server.getsockname()[1]
    with open(PORT_FILE, "w", encoding="utf-8") as f:
        f.write(str(current_port))

    print(
        f"{MAGENTA}===================================================={RESET}",
        flush=True,
    )
    print(
        f"{MAGENTA}    PROJECT FREEISM: PARTNER GUARD V28.9 (GAIA){RESET}", flush=True
    )
    print(
        f"{MAGENTA}===================================================={RESET}",
        flush=True,
    )
    print(
        f"{CYAN} 상태       : {GREEN}파트너의 주권 수호 중 (가동 중){RESET}", flush=True
    )
    print(f"{CYAN} 신호 포트   : {current_port}{RESET}", flush=True)
    print(
        f"{YELLOW} 알림       : 프리즘 파트너의 작업 신호를 대기 중...{RESET}",
        flush=True,
    )
    print(
        f"{MAGENTA}===================================================={RESET}\n",
        flush=True,
    )

    lock_all_sanctuaries()
    print(f"\n{GREEN}[완료] ACL 법전에 따른 모든 성역 물리적 봉인 완료.{RESET}")

    # 비대면 신호 감시자 기동 (V30.0)
    observer = Observer()
    observer.schedule(SynapseHandler(), PRISM_HOME, recursive=False)
    observer.start()
    print(f"{CYAN} 알림       : 비대면 신호(partner_synapse.json) 감시 가동 중...{RESET}", flush=True)

    threading.Thread(target=keyboard_listener, daemon=True).start()
    threading.Thread(target=synapse_interceptor_thread, daemon=True).start()
    
    try:
        agent_handler(server)
    finally:
        observer.stop()
        observer.join()


def cleanup():
    global running
    if not running:
        return
    running = False
    print(f"\n{YELLOW}[SHUTDOWN] 가디언을 종료하고 모든 성역을 정밀 해방합니다.{RESET}")
    try:
        if os.path.exists(ACL_FILE):
            with open(ACL_FILE, "r", encoding="utf-8") as f:
                acl = json.load(f)
            targets = set(acl.get("forbidden_all", []))
            for role in acl.get("roles", {}).values():
                targets.update(role.get("write_access", []))
            count = _process_lock_paths(targets, False)
            print(
                f"\n{GREEN}✔ [물리적 해방 확정] 총 {count}개 성역이 자유를 되찾았습니다.{RESET}"
            )
    except:
        _process_lock_paths(["./"], False)
    for f in [PORT_FILE, PID_FILE]:
        if os.path.exists(f):
            os.remove(f)
    print(f"{MAGENTA}[REPORT] 모든 빗장이 개방되었습니다. 제어권을 반환합니다.{RESET}")


if __name__ == "__main__":
    try:
        main()
    except:
        cleanup()
