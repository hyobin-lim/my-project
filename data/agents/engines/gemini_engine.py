import os
import google.generativeai as genai
from dotenv import load_dotenv
from .base import AIEngineBase

class GeminiEngine(AIEngineBase):
    def __init__(self, model_name='gemini-1.5-flash'):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)

    def generate(self, prompt: str, system_instruction: str = "") -> str:
        try:
            # 시스템 인스트럭션이 있는 경우 프롬프트에 결합 (Flash 모델 특성상)
            full_prompt = f"{system_instruction}\n\n[USER REQUEST]\n{prompt}" if system_instruction else prompt
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error in GeminiEngine: {str(e)}"

    def get_name(self) -> str:
        return f"Google Gemini ({self.model_name})"
