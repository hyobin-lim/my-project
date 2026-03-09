import os
import google.generativeai as genai
from dotenv import load_dotenv
from .base import AIEngineBase

class GeminiEngine(AIEngineBase):
    def __init__(self, model_name='models/gemini-2.0-flash'):
        # 경로 설정 및 .env 로드
        dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        load_dotenv(dotenv_path)
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found.")
        
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        # 에이전트별 기억 저장소 (Chat Sessions)
        self.sessions = {}

    def generate(self, prompt: str, system_instruction: str = "", session_id: str = "default") -> str:
        try:
            # 세션이 없으면 생성 (시스템 지침을 뇌에 박아넣음)
            if session_id not in self.sessions:
                print(f"[ENGINE] Initializing New Memory Session: {session_id}", flush=True)
                self.sessions[session_id] = self.model.start_chat(history=[])
                # 첫 메시지에 시스템 지침과 8대 문서를 '기억'으로 주입
                initial_context = f"SYSTEM INSTRUCTION: {system_instruction}\n\n당신은 사령부의 일원으로서 이 내용을 완벽히 숙지했습니다."
                self.sessions[session_id].send_message(initial_context)

            print(f"[GEMINI ENGINE] Thinking with Memory (Session: {session_id})...", flush=True)
            response = self.sessions[session_id].send_message(prompt)
            return response.text
        except Exception as e:
            print(f"[GEMINI ENGINE] Error: {e}", flush=True)
            return f"Error: {str(e)}"

    def get_name(self) -> str:
        return f"Google Gemini ({self.model_name})"
