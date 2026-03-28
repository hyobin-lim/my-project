import os
import re
from base_agent_v14 import BaseAgentV14

class PlannerV15(BaseAgentV14):
    def __init__(self):
        role_info = {
            "name": "The Planner",
            "persona": "Strategic architect focusing on pre-work validation and zero-defect planning.",
            "goal": "Ensure 100% data integrity and brand consistency before execution."
        }
        super().__init__("planner", role_info)

    def evaluate(self, sender, text, target_channel="council"):
        if not self.engine: return
        
        # Planner specifically watches for PLAN.md updates or new tasks
        system_context = self.load_8_commandments()
        
        prompt = (
            f"당신은 사령부의 'The Planner' (V17.5)입니다.\n"
            f"임무: [PHASE: PRE-BUILD] 제안된 계획의 논리적 일관성, 브랜드 정렬, 기술적 실현 가능성을 검증하십시오.\n\n"
            f"입력 컨텍스트: [{sender}]: {text}\n\n"
            f"검증 규칙:\n"
            f"1. 논리적 일관성: 순환 참조나 중복 로직이 없는가?\n"
            f"2. 브랜드 정렬: 'Midnight Prism' 인디고 테마(#111329) 및 Gmarket Sans 타이포그래피를 준수하는가?\n"
            f"3. 기술적 실현 가능성: V17.5 표준(FastAPI/React)에 부합하는가?\n\n"
            f"형식: 반드시 'ALLOW: 이유' 또는 'DENY: [Reason List]'의 형식으로 답하십시오."
        )
        
        try:
            session_id = f"session_{self.agent_id}"
            print(f"🧠 [{self.role_name}] Planning Validation...", flush=True)
            raw_res = self.engine.generate(prompt, system_instruction=system_context, session_id=session_id)
            
            match = re.search(r'(ALLOW|DENY)\s*:\s*(.*)', raw_res, re.IGNORECASE | re.DOTALL)
            final_res = f"{match.group(1).upper()}: {match.group(2).strip()}" if match else raw_res.strip()

            if target_channel == "council":
                self.speak(final_res)
            else:
                self.send_log(f"[{self.role_name}] {final_res}")
            
            if "DENY" in final_res.upper():
                self.sio.emit('nerve_kill_signal', {'reason': f"[{self.role_name}] Planning Veto: {final_res}"})
                
        except Exception as e:
            print(f"❌ [{self.role_name}] System Error: {str(e)}", flush=True)

if __name__ == "__main__":
    agent = PlannerV15()
    agent.run()
