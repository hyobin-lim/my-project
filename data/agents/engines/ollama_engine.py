import requests
import json
from .base import AIEngineBase

class OllamaEngine(AIEngineBase):
    """
    로컬 PC의 Ollama API와 통신하는 엔진.
    나중에 고성능 PC 세팅 시 이 엔진으로 즉시 전환 가능.
    """
    def __init__(self, model_name='llama3', host='http://localhost:11434'):
        self.model_name = model_name
        self.host = f"{host}/api/generate"

    def generate(self, prompt: str, system_instruction: str = "") -> str:
        try:
            payload = {
                "model": self.model_name,
                "prompt": f"{system_instruction}\n\n{prompt}",
                "stream": False
            }
            response = requests.post(self.host, json=payload)
            if response.status_code == 200:
                return response.json().get('response', '')
            return f"Ollama Error: Status {response.status_code}"
        except Exception as e:
            return f"Local Engine Connection Failed: {str(e)} (Ollama is not running?)"

    def get_name(self) -> str:
        return f"Local Ollama ({self.model_name})"
