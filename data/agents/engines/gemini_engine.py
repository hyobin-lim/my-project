import os
import time
from google import genai
from dotenv import load_dotenv
from .base import AIEngineBase

class GeminiEngine(AIEngineBase):
    def __init__(self, model_name='gemini-2.0-flash'):
        # 경로 설정 및 .env 로드
        dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        load_dotenv(dotenv_path)
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found.")
        
        # 최신 google.genai 클라이언트 설정
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        # 에이전트별 채팅 세션 저장소
        self.sessions = {}

    def generate(self, prompt: str, system_instruction: str = "", session_id: str = "default") -> str:
        max_retries = 3
        retry_delay = 5  # 429 에러 시 기본 대기 시간 (초)

        for attempt in range(max_retries):
            try:
                # 세션이 없으면 생성
                if session_id not in self.sessions:
                    print(f"[ENGINE] Initializing New GenAI Session: {session_id}", flush=True)
                    # 시스템 지침을 포함한 채팅 세션 시작
                    self.sessions[session_id] = self.client.chats.create(
                        model=self.model_name,
                        config={'system_instruction': system_instruction}
                    )
                    # 초기 지침 주입 (최초 1회)
                    initial_context = "당신은 사령부의 일원으로서 부여된 임무와 프로젝트의 8대 문서를 완벽히 숙지했습니다. 이제 활동을 시작하십시오."
                    self.sessions[session_id].send_message(initial_context)

                print(f"[GEMINI ENGINE] Thinking (Session: {session_id}, Attempt: {attempt+1})...", flush=True)
                response = self.sessions[session_id].send_message(prompt)
                return response.text

            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower():
                    print(f"[GEMINI ENGINE] Quota Exceeded (429). Retrying in {retry_delay}s... ({attempt+1}/{max_retries})", flush=True)
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 지수 백오프 적용
                else:
                    print(f"[GEMINI ENGINE] Critical Error: {e}", flush=True)
                    return f"Error: {error_str}"

        return "Error: Maximum retries exceeded due to API Quota limits."

    def get_name(self) -> str:
        return f"Google GenAI ({self.model_name})"
