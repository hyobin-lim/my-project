import time
import os
import shutil
import subprocess
import socketio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv
from engines.factory import get_engine

load_dotenv()

# 전역 설정
BACKUP_DIR = os.path.abspath("data/backups")
ACTION_LOG = os.path.abspath("data/logs/guardian_action.log")
IDENTITY_PATH = os.path.abspath("AI_CORE/IDENTITY.md")

class OmniscientGuardianV8(FileSystemEventHandler):
    def __init__(self):
        self.engine = get_engine()
        self.last_partner_msg = ""
        self.sio = socketio.Client()
        self.setup_socket()
        print(f"🛡️ Guardian V8.2 (Neural) initialized. Engine: {self.engine.get_name()}")

    def setup_socket(self):
        @self.sio.on('message_received')
        def on_message(data):
            # 파트너의 목소리를 실시간으로 직접 듣고 기억함 (메인 AI를 거치지 않음)
            if data.get('sender') == 'Partner':
                self.last_partner_msg = data.get('text', '')
                print(f"🛡️ Guardian heard Partner: '{self.last_partner_msg[:30]}...'")

        try:
            self.sio.connect('http://localhost:5000')
        except:
            print("🛡️ Connection to Dashboard failed. Running in standalone mode.")

    def on_modified(self, event):
        if event.is_directory: return
        path = os.path.abspath(event.src_path)
        if any(x in path for x in [".git", ".venv", "node_modules", "logs", "backups", "agents"]): return
        self.verify_and_protect(path)

    def verify_and_protect(self, path):
        try:
            time.sleep(0.2)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                new_content = f.read()
            
            # 실시간 감시 로직 (가장 최근 들은 파트너의 의도와 대조)
            with open(IDENTITY_PATH, "r", encoding="utf-8") as f:
                identity = f.read()
            
            prompt = f"메인 AI의 현재 작업물이 파트너의 최신 의도에 부합하는지 판정하십시오.\n\n[파트너의 의도]\n{self.last_partner_msg}\n\n[작업물]\n{new_content[:1500]}"
            system_instruction = f"당신은 전지적 가디언입니다. 헌법을 수호하십시오.\n\n[헌법]\n{identity}"
            
            res_text = self.engine.generate(prompt, system_instruction=system_instruction)
            
            if "[RECOVER]" in res_text:
                self.revert(path, f"Contradiction with Partner's real-time intent: {res_text[:50]}")
            
            # 금기 키워드 (생략 등) 즉시 차단
            for kw in ["...", "*(중략)*", "(기존 내용 동일)"]:
                if kw in new_content:
                    self.revert(path, f"Omission detected: {kw}")
                
        except Exception as e:
            print(f"Guardian Error: {e}")

    def revert(self, path, reason):
        filename = os.path.basename(path)
        snapshot_path = os.path.join(BACKUP_DIR, f"{filename}.bak")
        if os.path.exists(snapshot_path):
            shutil.copy2(snapshot_path, path)
            msg = f"🛡️ [REAL-TIME BLOCK] {filename} restored from backup. Reason: {reason}"
        else:
            # subprocess.run(["git", "restore", path], check=True, shell=True)  # 제거됨: 독단적 복구 금지
            msg = f"🛡️ [DETECTION] {filename} modification detected but no backup found. Reason: {reason}"
        
        print(f"\n\033[91m{msg}\033[0m")
        with open(ACTION_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
        
        # 차단 사실을 사령부에 방송
        if self.sio.connected:
            self.sio.emit('new_log', {'log': msg})

if __name__ == "__main__":
    if not os.path.exists(BACKUP_DIR): os.makedirs(BACKUP_DIR)
    observer = Observer()
    handler = OmniscientGuardianV8()
    observer.schedule(handler, ".", recursive=True)
    observer.start()
    try:
        while True: time.sleep(1)
    except: observer.stop()
    observer.join()
