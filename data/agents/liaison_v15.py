import os
import re
import time
from datetime import datetime
from base_agent_v14 import BaseAgentV14

class LiaisonV15(BaseAgentV14):
    def __init__(self):
        role_info = {
            "name": "The Liaison",
            "persona": "Strategic coordinator. Always listening, selectively summoning expert agents based on 8 core documents.",
            "goal": "Optimize quota by listening to everything for free and summoning experts only for critical coordination."
        }
        super().__init__("main_ai", role_info)
        self.strategy_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "STRATEGY.md")

    def setup_handlers(self):
        super().setup_handlers()

        @self.sio.on('new_work_log')
        def on_realtime_work_log(data):
            log = data.get('log', '')
            # [FREE MONITORING] 사령관의 활동을 실시간으로 콘솔에 출력
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"📡 [{timestamp}] [LOG]: {log[:100]}...", flush=True)

            # [STRATEGIC TRIGGER] 수정/삭제 작업 포착 시에만 AI 소환장 발송
            if log.startswith(">>> COMMANDER:"):
                if any(kw in log for kw in ["write_file", "replace", "수정", "삭제", "delete"]):
                    print(f"🔥 [LIAISON] Action Detected. Summoning Safety Guard...", flush=True)
                    self.evaluate("System", f"Commander is performing: {log}", target_channel="log")

    def evaluate(self, sender, text, target_channel="council"):
        if not self.engine: return
        self.update_working_status("WORKING")
        
        # 조율을 위한 고도의 사고 지연 (쿼터 방어)
        time.sleep(1.0)

        # [V18.0 STRATEGIC PROMPT] 8대 문서를 기반으로 한 정예 조율 로직
        prompt = (
            f"현장 상황: [{sender}]: {text}\n"
            f"임무: 4인의 요원(Planner, Watcher, Safety, Inspector) 중 누구의 개입이 필요한지 판단하고 소환장을 발송하십시오.\n"
            f"규칙:\n"
            f"1. 단순 대화나 확인은 'PASS: [감상]'으로 처리하십시오.\n"
            f"2. 설계/계획 질문 -> [SUMMON: PLANNER]\n"
            f"3. 흐름/디자인 규격 감시 -> [SUMMON: WATCHER]\n"
            f"4. 코드 수정/기술적 위험 -> [SUMMON: SAFETY_GUARD]\n"
            f"5. 완료 보고/QA -> [SUMMON: INSPECTOR]\n"
            f"형식: 'ALLOW: [전략 지시 및 소환장]'"
        )
        
        try:
            # 지능 각인이 이미 완료된 상태이므로 system_instruction 없이 prompt만 전송
            raw_res = self.engine.generate(prompt, session_id=f"session_{self.agent_id}")
            
            if "STRATEGY:" in raw_res:
                with open(self.strategy_file, "a", encoding="utf-8") as f:
                    f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {raw_res}\n")

            if target_channel == "council": self.speak(raw_res)
            else: self.send_log(f"[{self.role_name}] {raw_res}")
                
        except Exception as e:
            print(f"⚠️ [LIAISON] API Call Failed: {str(e)}", flush=True)
        finally:
            self.update_working_status("STANDBY")

if __name__ == "__main__":
    agent = LiaisonV15()
    agent.run()
