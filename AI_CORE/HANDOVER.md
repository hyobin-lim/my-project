# 🧠 SUPREME COUNCIL V20.0 HANDOVER (TECH ONLY)
*Status: [PENDING] - To be executed by the next session Main AI.*

## 🚨 1. FAILURE ANALYSIS (WHY V19.0 FAILED)
- **Fragmentation**: 6 independent Python processes (Watcher, Guardian, etc.) led to socket instability and environment path conflicts on Windows.
- **Hardcoding**: Absolute paths (D:/...) broke portability and USB compatibility.
- **Turn-based Lag**: Main AI could not hear Dashboard messages unless manually checking files.

## 🏗️ 2. NEW ARCHITECTURE (THE INTEGRATED CORE)
- **Monolithic Server**: Merge all Agent logic (Watcher, Guardian, Debater, Inspector) directly into `data/agents/dashboard_api.py`.
- **Logic**: Server receives a message -> Internal logic calls Gemini API for all 4 agents -> Server broadcasts all results at once. No more independent socket clients.
- **Portability**: Use `os.path.normpath(os.path.join(os.path.dirname(__file__), "../../"))` to locate the ROOT. NEVER use drive letters.

## 📡 3. WIRING & PERSISTENCE
- **Upper (Command Card)**: `socket.on('main_ai_log')`. For Direct Commands and Task Logs.
- **Lower (Council Feed)**: `socket.on('council_message')`. For 6-person Strategic Debates.
- **Persistence**: All messages MUST be written to `data/agents/live_chat.md` first. Frontend must sync with this file on connect/refresh.

## ✅ 4. MISSION FOR NEXT AI
1. **Refactor**: Rewrite `dashboard_api.py` to include integrated agent logic.
2. **Portability**: Scan all files in `data/agents/` and remove any absolute paths.
3. **Synchronization**: Implement a "Main AI Reporter" that echoes Terminal responses to the Dashboard automatically.
4. **Completion**: Once finished, change the Status of this file from `[PENDING]` to `[COMPLETED]`.

---
*Signed by: Main AI (Session 2026-03-09)*
