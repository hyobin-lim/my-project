import time
import os
import glob
import google.generativeai as genai
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

DEBATE_FILE = os.path.abspath("data/agents/debate.txt")
LIVE_CHAT = os.path.abspath("data/agents/live_chat.md")
DOCS_DIR = os.path.abspath("프로젝트_기록")
IDENTITY_PATH = os.path.abspath("AI_CORE/IDENTITY.md")

class OmniscientDebaterV8(FileSystemEventHandler):
    """
    V8.0 전지적 디베이터: 실시간 대화 맥락을 숙지하여 더 하이엔드적인 대안을 제시함.
    """
    def on_modified(self, event):
        if os.path.abspath(event.src_path) == DEBATE_FILE:
            self.start_debate()

    def load_8_pillars(self):
        context = ""
        # 1. 헌법
        with open(IDENTITY_PATH, "r", encoding="utf-8") as f:
            context += f"--- [SUPREME CONSTITUTION] ---\n{f.read()}\n\n"
        # 2. 실시간 대화록
        with open(LIVE_CHAT, "r", encoding="utf-8") as f:
            context += f"--- [LIVE CHAT CONTEXT] ---\n{f.read()}\n\n"
        # 3. 역사
        doc_files = glob.glob(os.path.join(DOCS_DIR, "*.md"))
        for doc in sorted(doc_files):
            filename = os.path.basename(doc)
            with open(doc, "r", encoding="utf-8") as f:
                context += f"--- [HISTORY: {filename}] ---\n{f.read()}\n\n"
        return context

    def start_debate(self):
        try:
            with open(DEBATE_FILE, "r", encoding="utf-8") as f:
                topic = f.read().strip()
            if not topic: return

            print(f"\n🗣️  [Omniscient Debater V8.0] Strategizing based on live chat and pillars...")

            context = self.load_8_pillars()
            if not api_key: return

            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""당신은 전지적 디베이터입니다. 방금 나눈 실시간 대화의 맥락을 완벽히 숙지하여 전략적 비판을 수행하십시오.

[8대 성전 (宪法 + 실시간 대화 + 역사)]
{context[-18000:]}

[현재 토론 주제]
{topic}

[임무]
1. 파트너가 방금 강조한 '실시간 의도'가 설계에 잘 반영되었는가?
2. 메인 AI의 제안이 혹시 게으르거나 축약된 방향은 아닌가?
3. '데이터 실재론'에 근거한 더 하이엔드적인 대안을 제시하라.

비판은 독설적이어야 하며, 파트너의 의도를 120% 충족하는 대안을 내놓으십시오."""
            
            res = model.generate_content(prompt)
            print(f"\n🗣️  [Debater Insight]\n{res.text}\n")
        except Exception as e:
            print(f"Debater Error: {e}")

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(OmniscientDebaterV8(), os.path.dirname(DEBATE_FILE), recursive=False)
    print("\n🗣️  Omniscient Debater V8.0 ACTIVE. (8-Pillar Strategy)\n")
    observer.start()
    try:
        while True: time.sleep(1)
    except: observer.stop()
    observer.join()
