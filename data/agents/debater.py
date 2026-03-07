import time
import os
import socketio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv
from engines.factory import get_engine

load_dotenv()

DEBATE_FILE = os.path.abspath("data/agents/debate.txt")
IDENTITY_PATH = os.path.abspath("AI_CORE/IDENTITY.md")

class OmniscientDebaterV8(FileSystemEventHandler):
    def __init__(self):
        self.engine = get_engine()
        self.last_partner_msg = ""
        self.sio = socketio.Client()
        self.setup_socket()
        print(f"🗣️  Debater V8.2 (Neural) initialized. Engine: {self.engine.get_name()}")

    def setup_socket(self):
        @self.sio.on('message_received')
        def on_message(data):
            # 실시간으로 파트너의 말을 듣고 즉시 비판적 대안을 구상함
            if data.get('sender') == 'Partner':
                self.last_partner_msg = data.get('text', '')
                print(f"🗣️  Debater processing Partner's idea: '{self.last_partner_msg[:30]}...'")
                # 여기서 즉시 실시간 토론 내용을 생성하여 웹 대시보드에 뿌릴 수도 있음

        try:
            self.sio.connect('http://localhost:5000')
        except:
            print("🗣️  Connection to Dashboard failed.")

    def on_modified(self, event):
        if os.path.abspath(event.src_path) == DEBATE_FILE:
            self.start_debate()

    def start_debate(self):
        try:
            with open(DEBATE_FILE, "r", encoding="utf-8") as f:
                topic = f.read().strip()
            if not topic: return

            with open(IDENTITY_PATH, "r", encoding="utf-8") as f:
                identity = f.read()

            system_instruction = f"당신은 전지적 디베이터입니다. 파트너의 실시간 의도와 헌법을 바탕으로 비판하십시오.\n\n[파트너의 실시간 의도]\n{self.last_partner_msg}\n\n[헌법]\n{identity}"
            res_text = self.engine.generate(f"현재 주제: {topic}", system_instruction=system_instruction)
            
            print(f"\n🗣️  [Real-time Insight]\n{res_text}\n")
            
            if self.sio.connected:
                self.sio.emit('new_log', {'log': f"🗣️ Debater: {res_text[:100]}..."})
                
        except Exception as e:
            print(f"Debater Error: {e}")

if __name__ == "__main__":
    observer = Observer()
    handler = OmniscientDebaterV8()
    observer.schedule(handler, os.path.dirname(DEBATE_FILE), recursive=False)
    observer.start()
    try:
        while True: time.sleep(1)
    except: observer.stop()
    observer.join()
