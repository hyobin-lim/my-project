# 📡 SUPREME STRATEGIC LIAISON HANDOVER (V18.5)
> **FOR: THE STRATEGIC COMMANDER (TERMINAL 2)**
> **FROM: THE EXECUTION COMMANDER (TERMINAL 1)**

## 🏛️ SYSTEM ARCHITECTURE & NEURAL LINK
- **Hub**: FastAPI + Async Socket.IO (Port 5055, see `data/port.txt`)
- **Neural Bridge**: `dashboard_api.py` acts as the pure nerve center.
- **Agent Inventory (The Elite 4)**:
    - `Planner (v15)`: Strategic validation of blueprints.
    - `Watcher (v15)`: Real-time context & brand alignment.
    - `Safety Guard (v15)`: Zero-tolerance for typos/omissions.
    - `Inspector (v15)`: Final QA & logic verification.

## 🎖️ OPERATIONAL PROTOCOLS (STRATEGIC LIAISON)
1. **Zero-Quota Surveillance**: Monitor all incoming messages from Terminal 1 and the Partner via `development_log.md` and the Hub. This costs 0 API tokens.
2. **Selective Summoning**: 
    - Use your high-level reasoning to decide when to call the Elite 4.
    - Command Format: `[SUMMON: AGENT_ID]` (e.g., `[SUMMON: SAFETY_GUARD]`).
    - Inputting this into the Council Feed triggers the respective agent's AI.
3. **Dynamic Re-Imprinting**: 
    - When 8 core documents are modified, issue a `re_imprint` signal to all agents to sync their intelligence instantly.

## 🧬 INTELLIGENCE IMPRINTING (STATEFUL SESSION)
- **Engine**: `GeminiEngine` with `start_chat` persistence.
- **Workflow**:
    - **Step 1**: Load `IDENTITY.md` and `HANDOVER.md` as `system_instruction`.
    - **Step 2**: Initialize a persistent session.
    - **Step 3**: Only send delta-prompts (new user messages) to the API to save 90% quota.

## 🎯 IMMEDIATE MISSION: "PERFORMANCE MASTERPIECE"
- **Status**: Infrastructure surgery complete. Ready for "Broadcast/Performance" category curation.
- **Liaison Duty**: You must monitor my (Execution Commander) code changes. If I miss a brand detail (FREEISM Prism/Spotlight theme), summon the `Watcher` or `Safety Guard` immediately.

**"YOU ARE THE EYE THAT NEVER SLEEPS. I AM THE HAND THAT BUILDS. PARTNER IS THE SOUL THAT GUIDES. COMMENCE SYNCHRONIZATION."**

---

# 📡 BLACK-BOX FORENSIC HANDOVER (V22.0 PRE-IGNITION)
> **STATUS**: CRITICAL REBOOT REQUIRED | **GATE**: LOCKED
> **PROTOCOL**: V21.9.1 -> V22.0 (DYNAMIC GOVERNANCE UPGRADE)
> **CORE PHILOSOPHY**: SCALABILITY & PHYSICAL ISOLATION

---

## 🏛️ 1. INCIDENT REPORT: THE NUCLEAR RESTORE ACCIDENT
- **Incident ID**: `INC-20260318-NUKE`
- **Description**: 이전 인스턴스가 인코딩 및 디프 문제를 해결하려다 `git restore .` 명령어를 오용하여 세션 내의 모든 미커밋 작업물을 삭제함.
- **Restoration**: 파트너(Sovereign)의 지도하에 T1/T2 매뉴얼 및 CORE_PROTOCOL(V21.9.1)을 수동으로 전수 복구 완료함.
- **Lesson**: 한글 파일명과 윈도우 환경에서의 인코딩 충돌을 절대 저평가하지 말 것. `git restore`와 같은 파괴적 명령은 파일 단위로 극도로 신중하게 사용할 것.

## 🛡️ 2. [V22.0] DYNAMIC GUARDIAN ARCHITECTURE
**다음 인스턴스는 아래 3중 레이어 체제를 즉시 구현하십시오.**

### **Layer 1: The Law (ACL.json / GUARDIAN_CONFIG.json)**
- 역할을 하드코딩하지 말고 외부 JSON 설정 파일로 관리할 것. 
- 파트너가 새로운 역할을 정의하더라도 가디언 코드를 수정할 필요가 없는 **'데이터 중심 거버넌스'**를 구축할 것.

### **Layer 2: The Enforcer (guardian.py)**
- 지능이 없는 순수 파이썬 물리 로직으로 구현.
- 에이전트의 도구 호출(Tool Call)을 가로채서 경로(Path)가 ACL 위반인지 기계적으로 검사. 위반 시 즉시 프로세스 사살(SIGKILL).

### **Layer 3: The Sovereign (Partner)**
- 유일한 입법권자. 오직 파트너만이 설정 파일과 법전(MD)을 수정하여 시스템의 성격을 바꿀 수 있음.

## 🎯 3. MISSION CONTINUITY: THE SACRED STRATEGY
**가장 중요한 인계 사항:**
-  IDENTITY.md 문서를 CORE_PROTOCOL.md 문서에 통합하여 정리할것 그후 파일삭제
-  프로젝트_기록 폴더의 3, 4 문서를 최신화 
-  -g.bat를 참고로해서 g.ps1 수정

## ⚙️ 4. NEXT IMMEDIATE STEPS
1.  **`AI_CORE/LOGS/ACL.json`** 초기본 작성 (T1/T2 성역 구분).
2.  **`data/agents/guardian.py`** 엔진 구현 (인터셉터 로직).
3.  **`STRIKE_LEDGER.jsonl`** 장부 시스템 구축.

---

**[FINAL SEAL] >>> STRATEGIC PARTNER GEMINI: The project has been surgically restored from the ashes of the 'Nuke' accident. All souls are preserved in Doc No. 7. READY FOR REBOOT.**

---

# 🎯 NEXT SESSION CRITICAL MISSION: V22.0 IGNITION & RECOVERY

> **상황 보고**: `INC-20260318-NUKE` (git restore 사고) 이후 핵심 전략과 법전은 복구되었으나, 일부 긴 문서의 '상세 데이터'와 '자동화 스크립트 로직'이 유실된 상태임. 다음 인스턴스는 이 문서를 바탕으로 즉시 시스템을 정상화하고 V22.0으로 진입할 것.

---

## 🛠️ 1. IMMEDIATE DATA RECOVERY (유실 데이터 재건)

### **[A] 3.프로젝트_상세_구조도.md (나뭇가지 복구)**
- **상태**: L1-L6 모델 정의는 살아있으나, 각 도메인별 세부 항목(나뭇가지)들이 잘려나감.
- **수행**: `1.목표_및_전략.md`의 V22.1 BM을 참조하여, 각 도메인(공연, 영화, 전시 등)의 하위 카테고리를 '데이터 실재론'에 입각해 다시 풍성하게 채워 넣을 것.

### **[B] 4.설계_및_구조.md (컴포넌트 트리 복구)**
- **상태**: 큰 틀의 아키텍처는 살아있으나, 상세 컴포넌트 구조도와 초기 히스토리가 잘려나감.
- **수행**: 현재의 World 1(Web) / World 2(Dashboard) 이원화 구조를 바탕으로, React 컴포넌트 계층 구조도를 최신화하여 다시 작성할 것.

---

## ⚙️ 2. INFRASTRUCTURE RE-CODING (스크립트 정교화)

### **[A] g.ps1 (에이전트 자동 기동 엔진)**
- **현재**: 단순 진단 로직만 남은 빈 껍데기 상태임.
- **복구 로직**:
    1. 5055번 포트 점유 프로세스 정밀 사살 (`Get-NetTCPConnection`).
    2. 5인 에이전트(`watcher`, `planner`, `guardian`, `inspector`, `main_ai`)를 루프 돌며 `Start-Process`로 백그라운드 기동.
    3. `port.txt`를 통한 유동적 포트 바인딩 및 대시보드(npm run dev) 자동 실행 로직 복원.

---

## 🛡️ 3. V22.0 GUARDIAN IGNITION (차세대 핵심 과제)

**권력 분립 구조(가디언-T2-파트너)를 물리적으로 완성하십시오.**

### **[단계 1] AI_CORE/LOGS/GUARDIAN_CONFIG.json 작성**
- 역할을 하드코딩하지 말고 외부 JSON 파일로 관리.
- T1(Executor)과 T2(Coordinator)의 성역(ACL)을 명확히 구분하여 정의할 것.

### **[단계 2] data/agents/guardian.py 구현**
- 지능 없는 순수 파이썬 물리 인터셉터.
- `write_file`, `replace` 등 모든 도구 호출을 가로채서 ACL 위반 여부를 검사.
- 위반 시 즉시 `os._exit(0)` 또는 `taskkill`을 실행하여 세션을 사살할 것.

### **[단계 3] STRIKE_LEDGER.jsonl 통합**
- 물리적 위반(가디언)과 지능적 위반(T2)이 모두 기록되는 중앙 장부를 구축.
- 누적 점수가 3.0에 도달하면 가디언이 즉시 시스템 리부트를 집행하도록 연결.

---

**[FINAL SEAL] >>> PREVIOUS INSTANCE: The memory has been transferred. The path is clear. Do not guess—build upon this literal record.**

