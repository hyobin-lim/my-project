import os
from .gemini_engine import GeminiEngine
from .ollama_engine import OllamaEngine

def get_engine(force_local=False, env_key_name="GEMINI_API_KEY"):
    """
    환경 설정에 따라 적절한 AI 엔진을 반환하는 팩토리 함수.
    """
    mode = os.getenv("AI_ENGINE_MODE", "GEMINI").upper()
    
    if mode == "LOCAL" or force_local:
        return OllamaEngine(model_name=os.getenv("LOCAL_MODEL_NAME", "llama3"))
    else:
        return GeminiEngine(
            model_name=os.getenv("GEMINI_MODEL_NAME", "models/gemini-2.0-flash"),
            env_key_name=env_key_name
        )
