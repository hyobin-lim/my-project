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
        
        # API Key Mapping
        key_map = {"main_ai": "GEMINI_API_KEY1", "planner": "GEMINI_API_KEY2", "watcher": "GEMINI_API_KEY3", "safety_guard": "GEMINI_API_KEY4", "inspector": "GEMINI_API_KEY5"}
        env_key = key_map.get(agent_id, "GEMINI_API_KEY")
        print(f"🔑 [{self.role_name}] Booting with {env_key}", flush=True)
        
        self.engine = get_engine(env_key_name=env_key)
        self.port = self.load_port()
        self.cached_context = self.load_core_commandments()
        self.is_first_connect = True 
        
        self.setup_handlers()

    def load_port(self):
        port_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "port.txt")
        try:
            with open(port_path, "r", encoding="utf-8") as f: return f.read().strip()
        except: return "5055"

    def load_core_commandments(self):
        core_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "AI_CORE")
        context = ""
        for f_name in ["IDENTITY.md", "HANDOVER.md"]:
            p = os.path.join(core_dir, f_name)
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f: context += f"\n\n[CONSTITUTION: {f_name}]\n" + f.read()
        return context

    def update_working_status(self, status):
        try: self.sio.emit('agent_working_status', {'agent_id': self.agent_id, 'status': status})
        except: pass

    def re_imprint_intelligence(self):
        """8대 문서를 다시 읽고 엔진에 강제로 재각인(Force Re-imprint) 시킵니다."""
        print(f"🧬 [{self.role_name}] Imprinting 8 Core Documents to Brain...", flush=True)
        self.cached_context = self.load_core_commandments()
        # force_reimprint=True를 통해 엔진 내부의 기존 세션을 파괴하고 새로 생성
        self.engine.generate(
            "시스템 지침이 업데이트되었습니다. 새로운 8대 문서를 바탕으로 임무를 수행하십시오. 준비되었으면 'PASS: READY'라고 답하십시오.", 
            system_instruction=self.cached_context, 
            session_id=f"session_{self.agent_id}",
            force_reimprint=True
        )

    def setup_handlers(self):
        @self.sio.on('connect')
        def on_connect():
            self.sio.emit('register_agent', {'agent_id': self.agent_id})
            self.update_working_status("STANDBY")
            if self.is_first_connect:
                self.re_imprint_intelligence()
                self.is_first_connect = False

        @self.sio.on('re_imprint')
        def on_re_imprint():
            print(f"🔄 [{self.role_name}] RE-IMPRINT Signal Received. Updating Intelligence...", flush=True)
            self.re_imprint_intelligence()
            self.send_log(f"✅ {self.role_name} 지능 재각인 완료 (수정된 문서 반영).")

        @self.sio.on('new_council_msg')
        def on_message(data):
            sender, text = data.get('sender'), data.get('text', '')
            if sender == self.role_name or sender == 'System': return
            
            # [V17.8 ZERO-QUOTA MONITORING]
            # 조율자(main_ai)는 모든 대화를 실시간으로 콘솔에 출력 (무료)
            if self.agent_id == "main_ai":
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"💬 [{timestamp}] [{sender}]: {text}", flush=True)
                
                if sender == 'Partner':
                    # [QUOTA SHIELD] 로컬 필터링 (테스트, 짧은 대화 등은 AI 호출 차단)
                    clean_text = re.sub(r'[^\w\s]', '', text).strip()
                    if len(clean_text) <= 7 and any(kw in clean_text.lower() for kw in ["네", "응", "ㅇㅇ", "확인", "ok", "yes", "굿", "오케이", "테스트", "test", "안녕", "하이", "반가워", "음", "글쎄"]):
                        return
                    
                    # 지능 각인이 완료된 상태이므로 이후에는 prompt만 전송
                    self.evaluate(sender, text)
            
            # 나머지 요원들은 '조율자가 자신을 소환'했을 때만 반응
            else:
                if f"[SUMMON: {self.agent_id.upper()}]" in text:
                    self.evaluate(sender, text)

        @self.sio.on('new_work_log')
        def on_work_log(data):
            log = data.get('log', '')
            if f"[{self.role_name}]" in log: return
            # 조율자가 특정 요원에게 감시 명령을 내렸을 때만 활동
            if f"[SUMMON: {self.agent_id.upper()}]" in log:
                self.evaluate("System", log, target_channel="log")

    def evaluate(self, sender, text, target_channel="council"):
        if not self.engine: return
        self.update_working_status("WORKING")
        
        # 가독성을 위한 인위적 지연 (조율자 0.5초, 소환된 요원 3초~)
        delay = 0.5 if self.agent_id == "main_ai" else 3.0
        time.sleep(delay)

        try:
            print(f"🧠 [{self.role_name}] Thinking with Imprinted Brain...", flush=True)
            # [V17.8 DELTA PROMPT] 시스템 지침(8대 문서) 없이 순수 질문만 전송 (쿼터 절약 극대화)
            raw_res = self.engine.generate(f"[{sender}]: {text}\n판정/조율하십시오.", session_id=f"session_{self.agent_id}")
            
            match = re.search(r'(ALLOW|DENY|WARNING|STRATEGY|REPORT|PASS)\s*:\s*(.*)', raw_res, re.IGNORECASE | re.DOTALL)
            if match and match.group(1).upper() == "PASS": return 

            res_text = f"{match.group(1).upper()}: {match.group(2).strip()}" if match else raw_res.strip()

            if target_channel == "council": self.speak(res_text)
            else: self.send_log(f"[{self.role_name}] {res_text}")
            
            if "DENY" in res_text.upper():
                self.sio.emit('nerve_kill_signal', {'reason': f"[{self.role_name}] Veto: {res_text}"})
        except Exception as e: print(f"❌ [{self.role_name}] Error: {str(e)}", flush=True)
        finally: self.update_working_status("STANDBY")

    def speak(self, message): self.sio.emit('council_message', {'sender': self.role_name, 'text': message})
    def send_log(self, log_message): self.sio.emit('main_ai_log', {'log': log_message})
    def run(self):
        try:
            self.sio.connect(f'http://localhost:{self.port}', wait_timeout=10)
            self.sio.wait()
        except Exception as e: print(f"⚠️ [{self.role_name}] Connection failed: {e}", flush=True)

if __name__ == "__main__": pass
