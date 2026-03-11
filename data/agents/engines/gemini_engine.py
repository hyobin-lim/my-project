import os
import time
import random
from google import genai
from dotenv import load_dotenv
from .base import AIEngineBase

class GeminiEngine(AIEngineBase):
    def __init__(self, model_name='gemini-2.0-flash', env_key_name="GEMINI_API_KEY"):
        # 경로 설정 및 .env 로드
        dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        load_dotenv(dotenv_path)
        
        # 지정된 키로 먼저 시도하고, 없으면 기본 GEMINI_API_KEY 사용
        api_key = os.getenv(env_key_name, "").strip()
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY", "").strip()
            
        if not api_key:
            raise ValueError(f"Neither {env_key_name} nor GEMINI_API_KEY was found.")
        
        # 최신 google.genai 클라이언트 설정
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        # 에이전트별 채팅 세션 저장소 (메모리 상에서 유지)
        self.sessions = {}

    def generate(self, prompt: str, system_instruction: str = "", session_id: str = "default", force_reimprint: bool = False) -> str:
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # [V17.9 DYNAMIC RE-IMPRINTING] 강제 재각인 요청 시 기존 세션 삭제
                if force_reimprint and session_id in self.sessions:
                    print(f"🔄 [ENGINE] Re-imprinting Session: {session_id}", flush=True)
                    del self.sessions[session_id]

                # [V17.5 TPM OPTIMIZATION] 세션 생성 시 시스템 지침을 한 번만 주입
                if session_id not in self.sessions:
                    print(f"🧬 [ENGINE] Imprinting Intelligence to Session: {session_id}", flush=True)
                    self.sessions[session_id] = self.client.chats.create(
                        model=self.model_name,
                        config={'system_instruction': system_instruction}
                    )
                    # 초기 지침 주입 확인
                    response = self.sessions[session_id].send_message(prompt)
                    return response.text

                # 이미 세션이 있는 경우 (Follow-up 대화)
                print(f"🧠 [GEMINI ENGINE] Continuing (Session: {session_id}, Attempt: {attempt+1})...", flush=True)
                response = self.sessions[session_id].send_message(prompt)
                return response.text

            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower():
                    # [V17.5 JITTER] 5~15초 사이의 랜덤 대기 시간 부여 (충돌 원천 차단)
                    jitter_delay = random.uniform(5.0, 15.0) * (attempt + 1)
                    print(f"⚠️ [GEMINI ENGINE] Quota Hit (429). Jitter Wait {jitter_delay:.1f}s... ({attempt+1}/{max_retries})", flush=True)
                    time.sleep(jitter_delay)
                else:
                    print(f"❌ [GEMINI ENGINE] API Error: {error_str}", flush=True)
                    return f"Error: {error_str}"

        return "Error: Maximum retries exceeded due to API Quota limits."

    def get_name(self) -> str:
        return f"Google GenAI ({self.model_name})"
