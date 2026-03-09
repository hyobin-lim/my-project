import os
import google.generativeai as genai
from dotenv import load_dotenv

def check_models():
    load_dotenv('data/agents/.env')
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    genai.configure(api_key=api_key)
    
    print("--- Available Models ---")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except Exception as e:
        print(f"Error listing models: {str(e)}")

if __name__ == "__main__":
    check_models()
