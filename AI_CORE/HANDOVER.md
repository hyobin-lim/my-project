# 🧠 SUPREME COUNCIL V14.4 HANDOVER (HORIZONTAL NEURAL NETWORK)
*Status: [SUCCESS - OPERATIONAL]*

## 🚀 1. MISSION ACCOMPLISHED: THE GREAT DEPARTURE
- **Achievement**: Terminal independence is 100% complete. The Main AI is now a background daemon (`main_ai_v14.py`) running in a separate `.venv` process.
- **Architecture**: Pure Socket-based communication. No more `live_chat.md` or `task.txt` for inter-agent talk.
- **Horizontal Autonomy**: All 5 agents connect independently to the Hub on Port 5055+ (Auto-detected).

## 🏗️ 2. VIRTUAL NEURAL STUDIO OPERATION GUIDE
1.  **Boot Sequence**: Run `./g.ps1`.
    - Hub starts -> Claims a free port -> Writes to `data/port.txt`.
    - 5 Agents read `port.txt` -> Connect via independent socket sessions.
    - Dashboard starts -> Reads port via env var -> Connects to Hub.
2.  **Staggered Intelligence**: 
    - Agents respond with 1s~9s delays to prevent **429 Quota Errors**.
    - If a 429 error occurs, it is caught and reported ONLY to the **Command Center Log**, keeping the **Council Feed** clean.
3.  **Data Realism UI**:
    - LEDs and Member List in the dashboard are 1:1 synced with real socket connections.
    - If an agent process dies, the LED turns off and the name becomes `--- EMPTY ---` immediately.

## 📡 3. COMMANDER'S MANUAL (FOR THE NEXT ME)
1.  **Never Use Files for Talk**: Communicate only via `sio.emit('council_message', ...)` for chat and `sio.emit('main_ai_log', ...)` for logs.
2.  **Channel Separation**: 
    - Commands from the Dashboard Left Card go to `new_work_log`.
    - Chat from the Dashboard Center Feed goes to `new_council_msg`.
3.  **No-Omit Policy**: Maintain the literal integrity of all files. Never use `...` or `(rest of code)`.
4.  **Append-Only Rule**: Always append new logs/updates to the bottom of documents in `프로젝트_기록/`.

---
*Signed by: Main AI (Session 2026-03-10) - "Free from the terminal, united in the socket, and driven by data realism."*
