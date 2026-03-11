import os
import datetime
import json
import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.error")

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*", ping_timeout=60, ping_interval=25)
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
sio_app = socketio.ASGIApp(sio, app)

AGENTS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(AGENTS_DIR)
PORT_FILE_PATH = os.path.join(DATA_DIR, "port.txt")

active_agents = {}
agent_statuses = {}

@app.post("/api/shutdown")
async def api_shutdown():
    """비상용 REST API 종료 엔드포인트"""
    logger.warning("🔴 SHUTDOWN SIGNAL RECEIVED VIA REST API")
    asyncio.create_task(delayed_shutdown())
    return {"status": "shutdown_initiated"}

async def delayed_shutdown():
    await asyncio.sleep(1)
    os._exit(0)

@sio.event
async def connect(sid, environ):
    await sio.emit('agent_status_update', {'active_agents': list(active_agents.values()), 'agent_statuses': agent_statuses}, to=sid)

@sio.event
async def disconnect(sid):
    if sid in active_agents:
        agent_id = active_agents[sid]
        del active_agents[sid]
        if agent_id in agent_statuses: del agent_statuses[agent_id]
        await sio.emit('agent_status_update', {'active_agents': list(active_agents.values()), 'agent_statuses': agent_statuses})

@sio.on('register_agent')
async def handle_register(sid, data):
    agent_id = data.get('agent_id')
    active_agents[sid] = agent_id
    if agent_id not in agent_statuses: agent_statuses[agent_id] = "STANDBY"
    logger.info(f"🟢 AGENT REGISTERED: {agent_id} (SID: {sid})")
    await sio.emit('agent_status_update', {'active_agents': list(active_agents.values()), 'agent_statuses': agent_statuses})

@sio.on('agent_working_status')
async def handle_working_status(sid, data):
    agent_id = data.get('agent_id')
    status = data.get('status')
    agent_statuses[agent_id] = status
    # WORKING 상태일 때만 로그 출력 (노이즈 방지)
    if status == "WORKING":
        logger.info(f"🔥 AGENT ACTIVE: {agent_id}")
    await sio.emit('agent_status_update', {'active_agents': list(active_agents.values()), 'agent_statuses': agent_statuses})

@sio.on('council_message')
async def handle_council(sid, data):
    sender, text = data.get('sender', 'Unknown'), data.get('text', '')
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    logger.info(f"💬 [COUNCIL] {sender}: {text[:50]}...")
    await sio.emit('new_council_msg', {'sender': sender, 'text': text, 'timestamp': timestamp})

@sio.on('main_ai_log')
async def handle_work_log(sid, data):
    log_text = data.get('log', '')
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    # 단순 모니터링 로그는 제외하고 중요한 로그만 서버 콘솔에 표시
    if "SUMMON" in log_text or "Veto" in log_text:
        logger.warning(f"🚨 [ALERT] {log_text}")
    await sio.emit('new_work_log', {'log': log_text, 'timestamp': timestamp})

@sio.on('system_shutdown')
async def handle_shutdown(sid):
    logger.warning("🔴 SHUTDOWN SIGNAL RECEIVED VIA SOCKET")
    os._exit(0)

@sio.on('re_imprint')
async def handle_re_imprint(sid, data=None):
    logger.warning("🔄 RE-IMPRINT SIGNAL RECEIVED. Broadcasting to all agents...")
    await sio.emit('re_imprint')

if __name__ == "__main__":
    with open(PORT_FILE_PATH, "w", encoding="utf-8") as f: f.write("5055")
    # access_log=False를 통해 불필요한 통신 노이즈를 제거하고 정예 로그만 출력
    uvicorn.run(sio_app, host='0.0.0.0', port=5055, log_level="info", access_log=False)
