import os
import datetime
import json
import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
import uvicorn

# 로깅 설정 (노이즈 제거)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.error")
# Werkzeug/Flask 로그와 달리 Uvicorn은 표준 로깅을 사용함

# 1. Socket.IO ASGI 서버 설정 (현대적 방식)
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins="*",
    ping_timeout=60,
    ping_interval=25
)

# 2. FastAPI 앱 생성 및 Socket.IO 통합
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO를 ASGI 앱으로 래핑
sio_app = socketio.ASGIApp(sio, app)

# --- 물리적 경로 설정 ---
AGENTS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(AGENTS_DIR)
PORT_FILE_PATH = os.path.join(DATA_DIR, "port.txt")

# 실시간 에이전트 인벤토리
active_agents = {}

def save_active_port(port):
    try:
        with open(PORT_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(str(port))
    except: pass

# --- Socket.IO 이벤트 핸들러 (비동기) ---

@sio.event
async def connect(sid, environ):
    logger.info(f"[CONN] New session: {sid}")
    await sio.emit('agent_status_update', {'active_agents': list(active_agents.values())}, to=sid)

@sio.event
async def disconnect(sid):
    if sid in active_agents:
        agent_id = active_agents[sid]
        del active_agents[sid]
        logger.info(f"[OFFLINE] {agent_id}")
        await sio.emit('agent_status_update', {'active_agents': list(active_agents.values())})

@sio.on('register_agent')
async def handle_register(sid, data):
    agent_id = data.get('agent_id')
    active_agents[sid] = agent_id
    logger.info(f"[LOGIN] {agent_id} is now online.")
    await sio.emit('agent_status_update', {'active_agents': list(active_agents.values())})

@sio.on('council_message')
async def handle_council(sid, data):
    sender = data.get('sender', 'Unknown')
    text = data.get('text', '')
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    await sio.emit('new_council_msg', {
        'sender': sender, 
        'text': text, 
        'timestamp': timestamp
    })

@sio.on('main_ai_log')
async def handle_work_log(sid, data):
    log_text = data.get('log', '')
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    await sio.emit('new_work_log', {'log': log_text, 'timestamp': timestamp})

@sio.on('system_shutdown')
async def handle_shutdown(sid):
    logger.info("\n[!] SHUTDOWN SIGNAL RECEIVED FROM DASHBOARD.")
    await sio.emit('system_shutdown_ack', {'status': 'success'})
    # 비동기 환경에서의 종료 처리
    await asyncio.sleep(0.5)
    os._exit(0)

if __name__ == "__main__":
    active_port = 5055
    save_active_port(active_port)
    
    print("=========================================================")
    print(f"   SUPREME COUNCIL NERVE HUB V14.7 (MODERN ASGI)")
    print(f"   - Engine: FastAPI + Uvicorn")
    print(f"   - Status: High-Performance Async Mode")
    print("=========================================================\n")

    # uvicorn으로 ASGI 앱 실행
    uvicorn.run(sio_app, host='0.0.0.0', port=active_port, log_level="error")
