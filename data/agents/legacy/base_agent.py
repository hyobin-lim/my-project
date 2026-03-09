import time
import os
import requests
import socketio
import google.generativeai as genai
from dotenv import load_dotenv

def find_dotenv():
    """현재 위치에서 상위로 올라가며 .env 파일을 찾음"""
    curr = os.path.abspath(__file__)
    for _ in range(5):
        curr = os.path.dirname(curr)
        potential = os.path.join(curr, ".env")
        if os.path.exists(potential):
            return potential
    return None

DOTENV_PATH = find_dotenv()
load_dotenv(DOTENV_PATH)
api_key = os.getenv("GEMINI_API_KEY")

# 설정 경로 (ROOT 기준으로 재설정)
ROOT_DIR = os.path.dirname(DOTENV_PATH) if DOTENV_PATH else os.getcwd()
IDENTITY_PATH = os.path.join(ROOT_DIR, "AI_CORE", "IDENTITY.md")
API_URL = "http://localhost:5000/api/chat"

class SupremeAgentV19:
    def __init__(self, agent_id, persona_prompt):
        self.agent_id = agent_id
        self.persona_prompt = persona_prompt
        self.sio = socketio.Client()
        self.is_ai_ready = False
        self.init_ai()
        self.setup_socket()

    def init_ai(self):
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.is_ai_ready = True
                print(f"✅ [{self.agent_id}] Intelligence Engine Armed.")
            except: self.is_ai_ready = False
        else:
            print(f"❌ [{self.agent_id}] API Key NOT FOUND in {DOTENV_PATH}")

    def setup_socket(self):
        @self.sio.on('connect')
        def on_connect():
            status = "정상" if self.is_ai_ready else "마비"
            self.report_to_dashboard(f"✅ {self.agent_id.upper()} 입실 완료. (엔진: {status})")

        @self.sio.on('new_council_msg')
        def on_message(data):
            sender = data.get('sender')
            text = data.get('text', '')
            if sender == 'Partner' and self.is_ai_ready:
                # 에이전트별 순차적 응답
                delay = {"Watcher": 1, "Debater": 2, "Guardian": 3, "Inspector": 4}.get(self.agent_id, 1)
                time.sleep(delay)
                self.analyze_and_report(text)

        @self.sio.on('new_work_log')
        def on_log(data):
            log = data.get('log', '')
            if ">>> COMMANDER:" in log and self.is_ai_ready:
                text = log.replace(">>> COMMANDER:", "").strip()
                self.analyze_and_report(f"[명령창] {text}")

        try:
            self.sio.connect('http://localhost:5000')
        except: pass

    def report_to_dashboard(self, text):
        try:
            requests.post(API_URL, json={"sender": self.agent_id, "text": text})
        except: pass

    def analyze_and_report(self, partner_text):
        if not self.is_ai_ready: return
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            with open(IDENTITY_PATH, "r", encoding="utf-8") as f:
                identity = f.read()
            prompt = f"당신은 {self.persona_prompt}입니다. 사령관님의 다음 말씀에 대해 1문장으로 짧고 강렬하게 응답하십시오.\n\n[헌법]\n{identity}\n\n[사령관님의 말씀]\n{partner_text}"
            res = model.generate_content(prompt)
            self.report_to_dashboard(res.text)
        except: pass

def run_agent(agent_id, persona):
    agent = SupremeAgentV19(agent_id, persona)
    try:
        while True: time.sleep(1)
    except: agent.sio.disconnect()

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        run_agent(sys.argv[1], sys.argv[2])
