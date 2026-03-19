import os
import sys
import time
import psutil
import atexit
import signal

# 색상 코드
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def get_gemini_processes():
    targets = []
    my_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['pid'] == my_pid: continue
            cmdline = " ".join(proc.info['cmdline'] or []).lower()
            if ("gemini" in cmdline or "launch_agent.ps1" in cmdline) and "code" not in (proc.info['name'] or "").lower():
                targets.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied): pass
    return targets

def surgical_strike():
    print(f"\n{RED}[!] GUARDIAN OFFLINE. TERMINATING ALL SECTORS...{RESET}")
    for p in get_gemini_processes():
        try: p.terminate()
        except: pass
    time.sleep(1)
    print(f"{GREEN}✅ Sector Secure.{RESET}")

atexit.register(surgical_strike)
signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
if hasattr(signal, 'SIGBREAK'): signal.signal(signal.SIGBREAK, lambda s, f: sys.exit(0))

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{MAGENTA}===================================================={RESET}")
    print(f"{MAGENTA}   🛡️  PROJECT FREEISM: GUARDIAN ENGINE V22.0{RESET}")
    print(f"{MAGENTA}===================================================={RESET}")
    print(f"{CYAN} STATUS      : {GREEN}ACTIVE & WATCHING{RESET}")
    print(f"{CYAN} JURISDICTION: {PROJECT_ROOT}{RESET}")
    print(f"{YELLOW} WARNING     : CLOSING THIS WINDOW KILLS ALL AGENTS{RESET}")
    print(f"{MAGENTA}===================================================={RESET}\n")
    
    print(f"{GREEN}[LIVE FEED]{RESET} Waiting for Agent spawn...")
    
    known_pids = set()
    try:
        while True:
            current_targets = get_gemini_processes()
            current_pids = {p.pid for p in current_targets}
            
            # 새로운 에이전트 감지 시 출력
            for p in current_targets:
                if p.pid not in known_pids:
                    print(f"{GREEN}[DETECTED]{RESET} Agent Spawned: PID {p.pid}")
                    known_pids.add(p.pid)
            
            # 종료된 에이전트 정리
            known_pids &= current_pids
            time.sleep(2)
    except KeyboardInterrupt: sys.exit(0)

if __name__ == "__main__":
    main()
