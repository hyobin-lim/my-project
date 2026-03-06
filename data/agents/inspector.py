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

TASK_FILE = os.path.abspath("data/agents/task.txt")
LIVE_CHAT = os.path.abspath("data/agents/live_chat.md")
DOCS_DIR = os.path.abspath("프로젝트_기록")
IDENTITY_PATH = os.path.abspath("AI_CORE/IDENTITY.md")

class OmniscientInspectorV8(FileSystemEventHandler):
    """
    V8.0 전지적 인스펙터: 실시간 대화의 '마지막 한마디'까지 체크하여 완벽한 이행 여부를 검수함.
    """
    def on_modified(self, event):
        if os.path.abspath(event.src_path) == TASK_FILE:
            self.verify_outcome()

    def load_8_pillars(self):
        context = ""
        with open(IDENTITY_PATH, "r", encoding="utf-8") as f:
            context += f"--- [SUPREME CONSTITUTION] ---\n{f.read()}\n\n"
        with open(LIVE_CHAT, "r", encoding="utf-8") as f:
            context += f"--- [LIVE CHAT CONTEXT] ---\n{f.read()}\n\n"
        doc_files = glob.glob(os.path.join(DOCS_DIR, "*.md"))
        for doc in sorted(doc_files):
            filename = os.path.basename(doc)
            with open(doc, "r", encoding="utf-8") as f:
                context += f"--- [HISTORY: {filename}] ---\n{f.read()}\n\n"
        return context

    def verify_outcome(self):
        try:
            time.sleep(1.0)
            with open(TASK_FILE, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            if len(lines) < 2: return
            
            command = lines[0]
            target_path = lines[1]
            if not os.path.exists(target_path): return

            print(f"\n⚖️  [Omniscient Inspector V8.0] Finalizing audit with real-time chat...")

            context = self.load_8_pillars()
            with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
                outcome = f.read()

            if not api_key: return

            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""당신은 전지적 인스펙터입니다. 8대 성전(특히 실시간 대화 내용)을 바탕으로 작업 결과를 무자비하게 검수하십시오.

[8대 성전 (Context)]
{context[-18000:]}

[명령 및 결과]
명령: {command}
결과 샘플: {outcome[-2500:]}

[검수 기준]
1. 방금 파트너와 나눈 '대화의 의도'를 100% 반영했는가?
2. 헌법에 명시된 '축약 금지'를 어기고 꼼수를 부리지는 않았는가?
3. 결과물에 생략의 흔적이 조금이라도 있는가?

판정은 [APPROVED] 혹은 [FAILED]로 시작하십시오."""
            
            res = model.generate_content(prompt)
            print(f"\n⚖️  [Inspector Verdict]\n{res.text}\n")
        except Exception as e:
            print(f"Inspector Error: {e}")

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(OmniscientInspectorV8(), os.path.dirname(TASK_FILE), recursive=False)
    print("\n⚖️  Omniscient Inspector V8.0 ACTIVE. (8-Pillar Audit)\n")
    observer.start()
    try:
        while True: time.sleep(1)
    except: observer.stop()
    observer.join()
