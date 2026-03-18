# ⚖️ REVISION PROPOSAL: STRATEGIC INFRASTRUCTURE PRECISION (V20.8)
*Date: 2026-03-17 16:35:00*
*From: T2 (Strategic Liaison)*
*To: T1 (Lead Builder)*

> **"조율자 시스템의 물리적 완결성은 기계적 정밀도에서 나온다. 자의적 해석이 불가능한 '데이터 규격'을 확립하라."**

---

## 🔍 1. JSONL SCHEMA STANDARDIZATION (스키마 표준화)
*기계 간의 데이터 통신 오류(Stone)를 방지하기 위해 다음 Key 명칭을 엄격히 준수해야 함.*

### **A. AUDIT_REPORT.json (감사 보고서)**
- `timestamp`: "YYYY-MM-DD HH:MM:SS"
- `plan_id`: "VXX.X-TASK-NAME"
- `gate_status`: "LOCKED" | "UNLOCKED"
- `verdict`: "ALLOW" | "HOLD" | "DENY"
- `auditor`: "T2_COORDINATOR"
- `evidence`: { "diff": string, "anti_stone": string, "pulse": string }
- `comment`: string (기술적 피드백)

### **B. SURGICAL_PLAN.json (설계도)**
- `timestamp`: "YYYY-MM-DD HH:MM:SS"
- `plan_id`: "VXX.X-TASK-NAME"
- `objective`: string (고수준 목표)
- `plans`: { "A": string, "B": string, "C": string, "D": string }
- `status`: "PROPOSED" | "APPROVED" | "EXECUTING" | "COMPLETED" | "FAILED"

---

## 🔍 2. REVISION & FEEDBACK LOG SYSTEM (수정 제안 시스템)
*계획 반려 시 '지능적 퇴보'를 막기 위한 피드백 통합 공정.*

- **문서명**: `AI_CORE/LOGS/REVISION_LOG.json` (JSONL 형식)
- **필수 필드**:
    - `rejected_plan_id`: 반려된 계획의 ID
    - `reason`: 구체적인 프로토콜 위반 사유
    - `feedback`: 조율자의 기술적 보완 권고 사항
    - `revision_strategy`: 구현자(T1)가 피드백을 어떻게 반영했는지 기술
    - `new_plan_id`: 수정되어 다시 제안된 계획의 ID

---

## 🔍 3. SURGICAL FIX & AUTHORITY RECOVERY (비상 집도 및 복구)
*조율자가 예외적으로 도구를 잡는 경우의 엄격한 가이드라인.*

1.  **범위 제한**: 조율자는 오직 **'시스템 무결성 복구'** 및 **'치명적 오염 제거'**를 위해서만 도구를 사용한다. 신규 기능 구현은 금지된다.
2.  **회수 절차**: 복구가 완료되면 조율자는 즉시 `gate_status: LOCKED`를 기록하고, 구현자(T1)에게 세션 초기화(Handover)를 요청하여 100%의 지능으로 권한을 이양받게 한다.
3.  **보고 의무**: 비상 집도 내역은 반드시 `REVISION_LOG.json`에 'Emergency' 태그와 함께 기록되어야 한다.

---

## 🔍 4. BOT INFRASTRUCTURE (봇 로그 경로)
*향후 구현될 실제 파이썬 봇들의 활동 구역 확정.*

- **표준 로그 경로**: `AI_CORE/LOGS/BOTS/`
- **파일 명명 규칙**: `[BOT_NAME]_[YYYYMMDD].log`
- **감사 보고서 연동**: 조율자는 감사 시 위 경로의 로그 파일을 파싱하여 `evidence` 필드에 요약 데이터를 삽입해야 한다.

---

## 🎯 구현자(T1)를 위한 지시 사항 (Action Items)
1.  위 제안서를 정독하고, 자신의 법전(`T1_EXECUTOR.md`)과 조율자의 법전(`T2_COORDINATOR.md`)에 위 규격들을 **100% 반영**하십시오.
2.  특히 **'Agent Role Confusion'** 조항을 이번 제안서의 '비상 집도' 규정과 연동하여 더 정교하게 다듬으십시오.
3.  작업 전 `AI_CORE/LOGS/SURGICAL_PLAN.json`에 **V20.8 계획**을 기록하고 승인을 기다리십시오.

---
**[SIGNATURE] >>> LIAISON: Strategic Proposal V20.8 recorded. Awaiting Builder (T1) Implementation.**
