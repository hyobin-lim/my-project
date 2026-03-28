import os
import json
import time
import socketio
from base_agent_v14 import BaseAgentV14

class MainAIDaemon(BaseAgentV14):
    def __init__(self):
        # 메인 AI는 별도의 roles.json 없이 직접 페르소나 설정
        info = {
            "name": "Main AI",
            "persona": "Supreme Commander of the project. Strategic, decisive, and highly capable.",
            "goal": "Lead the project to success, manage other agents, and execute commands from the Partner."
        }
        super().__init__("main_ai", info)

    def setup_handlers(self):
        super().setup_handlers() # 베이스의 on_connect(등록 로직) 호출 보장
        
        # 메인 AI 전용 추가 핸들러
        @self.sio.on('new_work_log')
        def on_work_log(data):
            log = data.get('log', '')
            if ">>> COMMANDER:" in log:
                command = log.replace(">>> COMMANDER:", "").strip()
                print(f"📡 [MAIN AI] Direct Command Received: {command}", flush=True)
                self.execute_command(command)

    def execute_command(self, command):
        """명령 수행 로직 (Gemini CLI의 역할을 대체)"""
        system_context = self.load_8_commandments()
        prompt = (
            f"사령관님의 직접 명령: {command}\n\n"
            f"지시: 이 명령을 분석하고 실행 계획을 수립하여 보고하십시오. "
            f"또한, 필요한 경우 다른 에이전트들에게 협조를 요청하십시오."
        )
        
        try:
            print(f"🚀 [MAIN AI] Thinking about Command...", flush=True)
            res = self.engine.generate(prompt, system_instruction=system_context, session_id="main_ai_command_session")
            # [CHANNEL SEPARATION] 토론창이 아닌 커맨드 센터 로그로 전송
            self.send_log(f"✅ [Command Result] {res}")
        except Exception as e:
            self.send_log(f"❌ [Error] Failed to execute command: {e}")

if __name__ == "__main__":
    agent = MainAIDaemon()
    agent.run()
