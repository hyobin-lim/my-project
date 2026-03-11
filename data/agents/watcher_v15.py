import os
import re
from base_agent_v14 import BaseAgentV14

class WatcherV15(BaseAgentV14):
    def __init__(self):
        role_info = {
            "name": "The Flow Watcher",
            "persona": "Contextual surveillance expert focused on real-time task alignment and brand standards.",
            "goal": "Detect context drift and ensure visual identity adherence during implementation."
        }
        super().__init__("watcher", role_info)

    def evaluate(self, sender, text, target_channel="council"):
        if not self.engine: return
        
        system_context = self.load_8_commandments()
        
        prompt = (
            f"당신은 사령부의 'The Flow Watcher' (V17.5)입니다.\n"
            f"임무: [PHASE: IN-BUILD CONTEXT] 실시간 진행 상황을 감시하고 논리적/미적 이탈을 감지하십시오.\n\n"
            f"입력 컨텍스트: [{sender}]: {text}\n\n"
            f"검증 규칙:\n"
            f"1. 컨텍스트 이탈(Context Drift): 현재 작업이 승인된 PLAN.md에서 20% 이상 벗어나는가?\n"
            f"2. Prism 표준: 모든 CSS/TSX 수정사항이 시각적 정체성(Midnight Prism)을 준수하는가?\n\n"
            f"형식: 위반 시 'WARNING: [이유]', 통과 시 'ALLOW: [이유]' 형식으로 답하십시오."
        )
        
        try:
            session_id = f"session_{self.agent_id}"
            print(f"🧠 [{self.role_name}] Contextual Surveillance...", flush=True)
            raw_res = self.engine.generate(prompt, system_instruction=system_context, session_id=session_id)
            
            match = re.search(r'(ALLOW|WARNING)\s*:\s*(.*)', raw_res, re.IGNORECASE | re.DOTALL)
            final_res = f"{match.group(1).upper()}: {match.group(2).strip()}" if match else raw_res.strip()

            if "WARNING" in final_res.upper():
                self.send_log(f"⚠️ [{self.role_name}] Drift Detected: {final_res}")
                self.speak(final_res)
            else:
                if target_channel == "council":
                    self.speak(final_res)
                else:
                    self.send_log(f"[{self.role_name}] {final_res}")
                
        except Exception as e:
            print(f"❌ [{self.role_name}] System Error: {str(e)}", flush=True)

if __name__ == "__main__":
    agent = WatcherV15()
    agent.run()
