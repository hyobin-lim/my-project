import os
import re
import time
from datetime import datetime
from base_agent_v14 import BaseAgentV14

class CouncilOrchestratorV15(BaseAgentV14):
    def __init__(self):
        role_info = {
            "name": "Council Orchestrator",
            "persona": "Strategic moderator of the Supreme Council. Selectively summoning expert agents to maintain high-end standards.",
            "goal": "Optimize debate and task quality by summoning the right experts at the right time."
        }
        super().__init__("council_orchestrator", role_info)
        self.strategy_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "STRATEGY.md")

    def setup_handlers(self):
        super().setup_handlers()

        @self.sio.on('new_work_log')
        def on_realtime_work_log(data):
            log = data.get('log', '')
            # [COUNCIL ORCHESTRATOR MONITORING]
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"📡 [{timestamp}] [LOG]: {log[:100]}...", flush=True)

            # [STRATEGIC TRIGGER]
            if log.startswith(">>> COMMANDER:"):
                if any(kw in log for kw in ["write_file", "replace", "수정", "삭제", "delete"]):
                    print(f"🔥 [COUNCIL ORCHESTRATOR] Action Detected. Summoning Safety Guard...", flush=True)
                    self.evaluate("System", f"Commander is performing: {log}", target_channel="log")

    def evaluate(self, sender, text, target_channel="council"):
        if not self.engine: return
        self.update_working_status("WORKING")
        
        # 조율을 위한 고도의 사고 지연 (쿼터 방어)
        time.sleep(1.0)

        # [V18.0 STRATEGIC PROMPT]
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
            raw_res = self.engine.generate(prompt, session_id=f"session_{self.agent_id}")
            
            if "STRATEGY:" in raw_res:
                with open(self.strategy_file, "a", encoding="utf-8") as f:
                    f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {raw_res}\n")

            if target_channel == "council": self.speak(raw_res)
            else: self.send_log(f"[{self.role_name}] {raw_res}")
                
        except Exception as e:
            print(f"⚠️ [COUNCIL ORCHESTRATOR] API Call Failed: {str(e)}", flush=True)
        finally:
            self.update_working_status("STANDBY")

if __name__ == "__main__":
    agent = CouncilOrchestratorV15()
    agent.run()
