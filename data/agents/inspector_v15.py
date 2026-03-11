import os
import re
from base_agent_v14 import BaseAgentV14

class InspectorV15(BaseAgentV14):
    def __init__(self):
        role_info = {
            "name": "The Inspector",
            "persona": "Quality assurance officer focusing on post-work verification and project standards compliance.",
            "goal": "Verify 1:1 match between planning items and implementation results for 'Masterpiece' standard."
        }
        super().__init__("inspector", role_info)

    def evaluate(self, sender, text, target_channel="council"):
        if not self.engine: return
        
        # Inspector watches for task completion or final results
        system_context = self.load_8_commandments()
        
        prompt = (
            f"당신은 사령부의 'The Inspector' (V17.5)입니다.\n"
            f"임무: [PHASE: POST-BUILD] 작업 결과물이 계획(PLAN.md) 및 8대 문서의 마스터피스 규격을 준수하는지 최종 감사하십시오.\n\n"
            f"입력 컨텍스트: [{sender}]: {text}\n\n"
            f"검증 규칙:\n"
            f"1. 계획 이행률: 제안된 모든 계획 항목이 1:1로 정확하게 구현되었는가?\n"
            f"2. 마스터피스 기준: 특히 '공연' 카테고리의 데이터 정확도와 UI 완성도가 상용화 수준인가?\n"
            f"3. 프로젝트 표준: Midnight Prism 테마와 Gmarket Sans 타이포그래피가 모든 영역에 적용되었는가?\n\n"
            f"형식: 반드시 'ALLOW: 이유' 또는 'DENY: [Defect List]'의 형식으로 답하십시오."
        )
        
        try:
            session_id = f"session_{self.agent_id}"
            print(f"🧠 [{self.role_name}] Quality Inspection...", flush=True)
            raw_res = self.engine.generate(prompt, system_instruction=system_context, session_id=session_id)
            
            match = re.search(r'(ALLOW|DENY)\s*:\s*(.*)', raw_res, re.IGNORECASE | re.DOTALL)
            final_res = f"{match.group(1).upper()}: {match.group(2).strip()}" if match else raw_res.strip()

            if target_channel == "council":
                self.speak(final_res)
            else:
                self.send_log(f"[{self.role_name}] {final_res}")
            
            if "DENY" in final_res.upper():
                self.sio.emit('nerve_kill_signal', {'reason': f"[{self.role_name}] Inspection Veto: {final_res}"})
                
        except Exception as e:
            print(f"❌ [{self.role_name}] System Error: {str(e)}", flush=True)

if __name__ == "__main__":
    agent = InspectorV15()
    agent.run()
