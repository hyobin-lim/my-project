import os
import sys
from dotenv import load_dotenv

# Path setting to include engines folder
sys.path.append(os.path.join(os.getcwd(), 'data', 'agents'))
from engines.gemini_engine import GeminiEngine

def test_gemini():
    try:
        engine = GeminiEngine()
        print(f"Engine Initialized: {engine.get_name()}")
        res = engine.generate("Say 'System OK' if you are alive.")
        print(f"Gemini Response: {res}")
    except Exception as e:
        print(f"Critical Error: {str(e)}")

if __name__ == "__main__":
    test_gemini()
