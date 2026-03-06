import time
import os
import json
import shutil
import subprocess
import google.generativeai as genai
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# 전역 설정
PLAN_FILE = os.path.abspath("data/agents/plan.txt")
LIVE_CHAT = os.path.abspath("data/agents/live_chat.md")
BACKUP_DIR = os.path.abspath("data/backups")
ACTION_LOG = os.path.abspath("data/logs/guardian_action.log")
IDENTITY_PATH = os.path.abspath("AI_CORE/IDENTITY.md")

class OmniscientGuardianV8(FileSystemEventHandler):
    """
    V8.0 전지적 가디언: 실시간 대화록(live_chat.md)을 도청하여 파트너의 의도와 어긋나는 모든 행위를 차단함.
    """
    def on_modified(self, event):
        if event.is_directory: return
        path = os.path.abspath(event.src_path)
        
        # 감시 예외
        if any(x in path for x in [".git", ".venv", "node_modules", "logs", "backups", "agents", "plan.txt", "task.txt", "debate.txt"]):
            return
        
        self.verify_and_protect(path)

    def verify_and_protect(self, path):
        try:
            # 1. 계획 신선도 체크 (60초 타임아웃)
            plan_mtime = os.path.getmtime(PLAN_FILE)
            current_time = time.time()
            is_planned = (current_time - plan_mtime <= 60)
            
            if not is_planned:
                self.revert(path, "Stealth Modification: Plan is stale. Update plan.txt based on current chat!")
                return

            time.sleep(0.5) # 파일 쓰기 대기
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                new_content = f.read()
            
            filename = os.path.basename(path)
            snapshot_path = os.path.join(BACKUP_DIR, f"{filename}.bak")
            violations = []

            # 2. 실시간 대화록(live_chat.md) 및 헌법(IDENTITY.md) 기반 가치 판단
            if api_key:
                with open(IDENTITY_PATH, "r", encoding="utf-8") as f:
                    identity = f.read()
                with open(LIVE_CHAT, "r", encoding="utf-8") as f:
                    chat_log = f.read()
                
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""당신은 전지적 가디언입니다. 파트너와 메인 AI의 실시간 대화 내용을 바탕으로 다음 작업이 '기만'이나 '오류'인지 판정하십시오.
                
[제1 헌법]
{identity}

[실시간 대화록 (Live Chat Log)]
{chat_log[-5000:]}

[메인 AI의 현재 작업물]
{new_content[:1500]}

판정: 대화 내용이나 헌법에 어긋난다면 [RECOVER], 정상이라면 [SAFE]라고 답하십시오."""
                
                res = model.generate_content(prompt)
                if "[RECOVER]" in res.text:
                    violations.append(f"AI-Detected Contradiction with Live Chat: {res.text[:100]}")

            # 3. 금기 키워드 및 생략 감시
            forbidden = ["...", "*(중략)*", "(기존 내용 동일)", "unchanged"]
            for kw in forbidden:
                if kw in new_content:
                    violations.append(f"Omission Marker: '{kw}'")
            if "stone" in new_content.lower():
                violations.append("Stone Typo")

            if violations:
                self.revert(path, " | ".join(violations))
            else:
                shutil.copy2(path, snapshot_path)
                
        except Exception as e:
            pass

    def revert(self, path, reason):
        filename = os.path.basename(path)
        snapshot_path = os.path.join(BACKUP_DIR, f"{filename}.bak")
        if os.path.exists(snapshot_path):
            shutil.copy2(snapshot_path, path)
            msg = f"🛡️ [Omniscient Guardian V8.0] RECOVERY: {filename}. Reason: {reason}"
        else:
            subprocess.run(["git", "restore", path], check=True, shell=True)
            msg = f"🛡️ [Omniscient Guardian V8.0] RECOVERY from Git. Reason: {reason}"
        
        print(f"\n\033[91m[CRITICAL ALERT] {msg}\033[0m")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(ACTION_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {msg}\n")

if __name__ == "__main__":
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    observer = Observer()
    observer.schedule(OmniscientGuardianV8(), ".", recursive=True)
    print("\n🛡️ Omniscient Guardian V8.0 ACTIVE. (Eavesdropping on live_chat.md)\n")
    observer.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
