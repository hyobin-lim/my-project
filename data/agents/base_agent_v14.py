import os
import time
import json
import socketio
import re
from datetime import datetime
from engines.factory import get_engine

class BaseAgentV14:
    def __init__(self, agent_id, role_info):
        self.agent_id = agent_id
        self.role_name = role_info.get('name', agent_id)
        self.persona = role_info.get('persona', '')
        self.goal = role_info.get('goal', '')
        
        self.sio = socketio.Client()
        self.engine = get_engine()
        self.port = self.load_port()
        self.cached_context = None
        
        self.setup_handlers()

    def load_port(self):
        """data/port.txt에서 물리 포트를 로드"""
        port_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "port.txt")
        try:
            with open(port_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except:
            return "5055"

    def load_8_commandments(self):
        """8대 필수 문서를 로드 (엔진 주입용)"""
        if self.cached_context: return self.cached_context
        
        agents_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(os.path.dirname(agents_dir))
        core_dir = os.path.join(root_dir, "AI_CORE")
        docs_dir = os.path.join(root_dir, "프로젝트_기록")
        
        docs = [
            os.path.join(core_dir, "IDENTITY.md"),
            os.path.join(core_dir, "HANDOVER.md"),
            os.path.join(docs_dir, "1.목표_및_전략.md"),
            os.path.join(docs_dir, "2.참고_사이트_분석.md"),
            os.path.join(docs_dir, "3.프로젝트_상세_구조도.md"),
            os.path.join(docs_dir, "4.설계_및_구조.md"),
            os.path.join(docs_dir, "5.작업_현황_및_로그.md"),
            os.path.join(docs_dir, "6.트러블슈팅_및_교훈.md")
        ]
        
        context = ""
        for p in docs:
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    context += f"\n\n[DOCUMENT: {os.path.basename(p)}]\n" + f.read()
        
        self.cached_context = context
        return context

    def setup_handlers(self):
        @self.sio.on('connect')
        def on_connect():
            print(f"✅ [{self.role_name}] Connected to Nerve Hub.", flush=True)
            # [IMMEDIATE] 소켓 등록은 0초 만에 즉시 (UI LED 점등용)
            self.sio.emit('register_agent', {'agent_id': self.agent_id})
            
            # [LOG ONLY] 입실 인사는 토론창 노이즈를 줄이기 위해 로그 채널로만 전송
            self.send_log(f"⚡ {self.role_name} 에이전트가 사령부에 접속되었습니다. (Standby)")

        @self.sio.on('new_council_msg')
        def on_message(data):
            """토론창 메시지 처리 (AI 엔진 가동 - 지연 적용)"""
            sender = data.get('sender')
            text = data.get('text', '')
            if sender == self.role_name or sender in ['System']: return
            # 파트너나 메인 AI의 발언에만 반응 (지연 전략 유지)
            if sender in ['Partner', 'Main AI']:
                self.evaluate(sender, text, target_channel="council")

        @self.sio.on('new_work_log')
        def on_work_log(data):
            """커맨드 센터(로그) 메시지 처리"""
            log = data.get('log', '')
            if ">>> COMMANDER:" in log:
                command = log.replace(">>> COMMANDER:", "").strip()
                # 커맨드 센터 명령에 대해서도 모든 에이전트가 감시 수행
                self.evaluate("Partner", f"[COMMAND] {command}", target_channel="log")

    def evaluate(self, sender, text, target_channel="council"):
        if not self.engine: return
        
        # [429 PREVENTION] 응답 지연을 더 공격적으로 설정 (에이전트별 충돌 방지)
        delay = {"watcher": 1.0, "guardian": 3.0, "inspector": 5.0, "debater": 7.0, "main_ai": 9.0}.get(self.agent_id, 2.0)
        time.sleep(delay)

        system_context = self.load_8_commandments()
        prompt = (
            f"당신은 사령부의 에이전트 '{self.role_name}'입니다.\n"
            f"페르소나: {self.persona}\n"
            f"목표: {self.goal}\n\n"
            f"현재 이벤트: [{sender}]: {text}\n\n"
            f"지시: 당신의 페르소나와 8대 문서를 바탕으로 위 발언을 심사하십시오.\n"
            f"형식: 반드시 'ALLOW: 이유' 또는 'DENY: 이유'의 형식으로 답하십시오."
        )
        
        try:
            session_id = f"session_{self.agent_id}"
            print(f"🧠 [{self.role_name}] Analyzing in {target_channel}...", flush=True)
            raw_res = self.engine.generate(prompt, system_instruction=system_context, session_id=session_id)
            
            # [ERROR FILTERING] 만약 결과에 'Error'가 포함되어 있다면 토론창 전송 금지
            if "Error" in raw_res:
                self.send_log(f"⚠️ [{self.role_name}] API Quota/Error: {raw_res}")
                return

            match = re.search(r'(ALLOW|DENY)\s*:\s*(.*)', raw_res, re.IGNORECASE | re.DOTALL)
            final_res = f"{match.group(1).upper()}: {match.group(2).strip()}" if match else raw_res.strip()

            # [CHANNEL ISOLATION] 에러가 아닌 정상 판정만 해당 채널로 전송
            if target_channel == "council":
                self.speak(final_res)
            else:
                self.send_log(f"[{self.role_name}] {final_res}")
            
            if "DENY" in final_res.upper():
                self.sio.emit('nerve_kill_signal', {'reason': f"[{self.role_name}] Veto: {final_res}"})
        except Exception as e:
            # 예외 발생 시 절대로 speak하지 않음
            self.send_log(f"❌ [{self.role_name}] System Error: {str(e)}")

    def speak(self, message):
        self.sio.emit('council_message', {'sender': self.role_name, 'text': message})

    def send_log(self, log_message):
        """커맨드 센터(작업 로그)로만 메시지 전송"""
        self.sio.emit('main_ai_log', {'log': log_message})

    def run(self):
        try:
            self.sio.connect(f'http://localhost:{self.port}')
            self.sio.wait()
        except Exception as e:
            print(f"⚠️ [{self.role_name}] Connection failed: {e}", flush=True)

if __name__ == "__main__":
    # 이 파일은 직접 실행되지 않고 상속받은 파일에서 사용됩니다.
    pass
