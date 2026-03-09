import os
import datetime
import json
import time
import socket
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supreme-nerve-v14'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# --- 물리적 경로 설정 ---
AGENTS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(AGENTS_DIR)
PORT_FILE_PATH = os.path.join(DATA_DIR, "port.txt")
LIVE_CHAT_PATH = os.path.join(AGENTS_DIR, "live_chat.md")

# 실시간 에이전트 인벤토리 (SID: AgentID)
active_agents = {}

def get_free_port(start_port=5055):
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return port
            except socket.error:
                port += 1

def save_active_port(port):
    try:
        with open(PORT_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(str(port))
        print(f"[HUB] Active port {port} saved to {PORT_FILE_PATH}", flush=True)
    except: pass

@socketio.on('connect')
def handle_connect():
    print(f"[HUB] New session connected: {request.sid}", flush=True)

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in active_agents:
        agent_id = active_agents[request.sid]
        del active_agents[request.sid]
        print(f"[HUB] Agent Offline: {agent_id} (SID: {request.sid})", flush=True)
        socketio.emit('agent_status_update', {'active_agents': list(active_agents.values())})

@socketio.on('register_agent')
def handle_register(data):
    agent_id = data.get('agent_id')
    active_agents[request.sid] = agent_id
    print(f"[HUB] Agent Registered: {agent_id} (SID: {request.sid})", flush=True)
    # 현재 활성화된 모든 에이전트 목록을 대시보드에 전파
    socketio.emit('agent_status_update', {'active_agents': list(active_agents.values())})

@socketio.on('council_message')
def handle_council(data):
    sender = data.get('sender', 'Unknown')
    text = data.get('text', '')
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    socketio.emit('new_council_msg', {
        'sender': sender, 
        'text': text, 
        'timestamp': timestamp,
        'sid': request.sid
    })

@socketio.on('main_ai_log')
def handle_work_log(data):
    log = data.get('log', '')
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    socketio.emit('new_work_log', {'log': log, 'timestamp': timestamp})

@socketio.on('nerve_kill_signal')
def handle_kill(data):
    socketio.emit('nerve_kill_signal', data)

if __name__ == "__main__":
    active_port = get_free_port(5055)
    save_active_port(active_port)
    print(f"🚀 [SUPREME NERVE HUB V14.1] Operating on Port {active_port}", flush=True)
    socketio.run(app, port=active_port, debug=False, host='0.0.0.0')
