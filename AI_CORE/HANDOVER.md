# 🚀 TECHNICAL SPECIFICATION: SUPREME MODERNIZATION V14.7
Status: STABLE - MODERN ASGI ARCHITECTURE DEPLOYED

## 1. MISSION PHILOSOPHY
- **Terminal Me** (Node.js CLI) stays alive.
- **Daemon Me** (5 Python Agents) runs via **FastAPI + Uvicorn (ASGI)**.
- **Goal**: 100% Asynchronous, high-performance neural bridge with zero socket blocking.

## 2. G.PS1: THE SELF-HEALING BOOTSTRAPPER
`g.ps1` is now a diagnostic engine. It ensures the environment is perfect before launch.
- **Diagnostic**: Checks for `fastapi`, `uvicorn`, `socketio`, `google.genai`, `eventlet`(should be removed).
- **Auto-Repair**: If any modern package is missing, it nukes `.venv` and rebuilds it automatically with real-time progress visibility.
- **Escaping Rules**: In the Here-String (`@"` ... `"@`), always preserve `$Host`, `$agent`, `$p`, `$_` using backticks (`` ` ``).

## 3. DASHBOARD_API.PY: THE ASGI HUB
- **Framework**: FastAPI + `python-socketio[asyncio]`.
- **Server**: `uvicorn` (Port 5055).
- **Feature**: Native `async/await` support. No more `monkey_patch()`.
- **Logging**: Cleaned up. No more `127.0.0.1` spam.

## 4. SURGICAL SHUTDOWN PROTOCOL (IMPORTANT)
When the RED BUTTON is pressed in the Dashboard:
1. **Targeted Kill**: Closes ONLY browser tabs with "FREEISM" or "SUPREME COUNCIL" in title.
2. **Process Nuke**: Kills all `python.exe` and `node.exe` related to the project.
3. **Clean Exit**: The Master Hub window closes itself automatically (No `-NoExit` needed in final trigger).

## 5. BRAND IDENTITY: FREEISM
- **Name**: FREEISM (Free + Ism + Prism)
- **Theme**: Midnight Prism (Global BG: `#111329`)
- **Slogan**: "지갑은 [ , ] 영감은 [ ! ]"
- **Typography**: Gmarket Sans (800/200 contrast).

## 6. FINAL CHECKLIST FOR THE NEXT ME
1. **MCP Status**: GitHub MCP is connected via environment variables. Do NOT hardcode tokens.
2. **Web Sync**: The service site (`web/`) needs its theme synced with the Dashboard's Midnight Prism.
3. **Agent Logic**: Agents are in 'Standby'. Next task is implementing the **L5 Strategy Manual** (Grade S~D logic).

**STAY ON V14.7. NEVER REVERT TO FLASK/EVENTLET. FOLLOW THE DATA REALISM.**
