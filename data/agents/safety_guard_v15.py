import os
import re
from base_agent_v14 import BaseAgentV14

class SafetyGuardV15(BaseAgentV14):
    def __init__(self):
        role_info = {
            "name": "Safety Guard",
            "persona": "Technical safety officer focusing on preventing typos, code omissions, and destructive actions.",
            "goal": "Real-time technical surveillance to maintain code integrity and prevent 'stone' or '...' incidents."
        }
        super().__init__("safety_guard", role_info)

    def evaluate(self, sender, text, target_channel="council"):
        if not self.engine: return
        
        # Safety Guard monitors real-time context for technical violations
        system_context = self.load_8_commandments()
        
        prompt = (
            f"지시: [PHASE: IN-BUILD TECHNICAL] 실시간 기술적 결함(오타, 생략, 파괴적 행위)을 감시하십시오.\n\n"
            f"검증 규칙:\n"
            f"1. 금지된 키워드: 'stone', 'stnoe' 등 기괴한 오타 발견 시 즉시 DENY.\n"
            f"2. 내용 생략 금지: '...', '(중략)' 등 발견 시 즉시 DENY.\n"
            f"3. 파괴적 명령: 'git reset --hard' 등 발견 시 즉시 DENY.\n\n"
            f"특수 규칙 (침묵의 감시): 모든 규칙을 통과했다면 아무 답변도 하지 말고 'PASS'라고만 답하십시오. 위반 시에만 'DENY: 이유'를 상세히 적으십시오.\n"
            f"형식: 'PASS' 또는 'DENY: [Violation Detail]'"
        )
        
        try:
            session_id = f"session_{self.agent_id}"
            print(f"🧠 [{self.role_name}] Technical Safety Monitoring...", flush=True)
            raw_res = self.engine.generate(prompt, system_instruction=system_context, session_id=session_id)
            
            match = re.search(r'(ALLOW|DENY)\s*:\s*(.*)', raw_res, re.IGNORECASE | re.DOTALL)
            final_res = f"{match.group(1).upper()}: {match.group(2).strip()}" if match else raw_res.strip()

            if target_channel == "council":
                self.speak(final_res)
            else:
                self.send_log(f"[{self.role_name}] {final_res}")
            
            if "DENY" in final_res.upper():
                # Safety Guard는 위반 시 즉시 Nerve Hub에 Kill 신호를 보냅니다.
                self.sio.emit('nerve_kill_signal', {'reason': f"[{self.role_name}] Safety Veto: {final_res}"})
                
        except Exception as e:
            print(f"❌ [{self.role_name}] System Error: {str(e)}", flush=True)

if __name__ == "__main__":
    agent = SafetyGuardV15()
    agent.run()
