import abc

class AIEngineBase(abc.ABC):
    """
    모든 AI 엔진(Gemini, Ollama, Local LLM 등)의 표준 인터페이스.
    나중에 엔진을 갈아끼워도 에이전트 코드는 수정할 필요가 없게 함.
    """
    @abc.abstractmethod
    def generate(self, prompt: str, system_instruction: str = "") -> str:
        """텍스트 생성 요청"""
        pass

    @abc.abstractmethod
    def get_name(self) -> str:
        """엔진 이름 반환 (예: 'Gemini 1.5 Flash', 'Llama 3')"""
        pass
