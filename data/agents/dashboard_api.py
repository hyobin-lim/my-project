import os
import datetime
import json
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv

# AI 엔진 팩토리 임포트
try:
    from engines.factory import get_engine
except ImportError:
    # 경로 문제 방지 (상위 디렉토리에서 실행될 경우 대비)
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from engines.factory import get_engine

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'high-end-secret-key'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENTS_DIR = os.path.join(BASE_DIR, "data", "agents")
LOGS_DIR = os.path.join(BASE_DIR, "data", "logs")
LIVE_CHAT_PATH = os.path.join(AGENTS_DIR, "live_chat.md")
ACTION_LOG_PATH = os.path.join(LOGS_DIR, "guardian_action.log")

# 전역 엔진 인스턴스
current_engine = get_engine()

def read_file_safe(path, tail=None):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            if tail:
                return "".join(lines[-tail:])
            return "".join(lines)
    return ""

# --- HTTP API ---
@app.route("/api/status", methods=["GET"])
def get_status():
    return jsonify({
        "engine": current_engine.get_name(),
        "task": read_file_safe(os.path.join(AGENTS_DIR, "task.txt")),
        "plan": read_file_safe(os.path.join(AGENTS_DIR, "plan.txt")),
        "chat": read_file_safe(LIVE_CHAT_PATH, tail=100),
        "logs": read_file_safe(ACTION_LOG_PATH, tail=20).splitlines()
    })

# --- WebSocket Events (실시간 통신) ---
@socketio.on('connect')
def handle_connect():
    print(f"🔗 [CLIENT CONNECTED] Web Dashboard Syncing...")
    emit('status_update', {'engine': current_engine.get_name()})

@socketio.on('send_message')
def handle_message(data):
    """
    웹에서 보낸 메시지를 처리하고 AI의 응답을 실시간으로 중계함.
    """
    message = data.get('message', '')
    if not message: return

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. 파트너 메시지 기록
    with open(LIVE_CHAT_PATH, "a", encoding="utf-8") as f:
        f.write(f"\n**파트너 (Web)**: {message} ({timestamp})\n")
    
    emit('message_received', {'sender': 'Partner', 'text': message, 'time': timestamp}, broadcast=True)

    # 2. 메인 AI (혹은 에이전트) 응답 시뮬레이션/처리
    # 여기서는 현재 설정된 엔진(Gemini/Local)을 사용하여 즉각적인 응답을 생성할 수 있음.
    # 나중에 메인 루프와 연동 시 이 부분에서 응답을 중계함.
    
    print(f"📩 [MESSAGE] Partner: {message}")

@socketio.on('switch_engine')
def handle_switch_engine(data):
    """실시간 엔진 스위칭 (Gemini ↔ Local)"""
    global current_engine
    mode = data.get('mode', 'GEMINI')
    os.environ["AI_ENGINE_MODE"] = mode
    current_engine = get_engine()
    
    msg = f"🔄 [ENGINE SWITCHED] Now using: {current_engine.get_name()}"
    print(msg)
    emit('status_update', {'engine': current_engine.get_name()}, broadcast=True)

# 로그 파일 감시 및 실시간 전송 (간단한 구현)
def tail_logs():
    last_size = 0
    if os.path.exists(ACTION_LOG_PATH):
        last_size = os.path.getsize(ACTION_LOG_PATH)
    
    while True:
        socketio.sleep(1)
        if os.path.exists(ACTION_LOG_PATH):
            current_size = os.path.getsize(ACTION_LOG_PATH)
            if current_size > last_size:
                with open(ACTION_LOG_PATH, "r", encoding="utf-8") as f:
                    f.seek(last_size)
                    new_logs = f.read().splitlines()
                    for log in new_logs:
                        socketio.emit('new_log', {'log': log})
                last_size = current_size

if __name__ == "__main__":
    # 백그라운드에서 로그 감시 시작
    socketio.start_background_task(tail_logs)
    
    print(f"\n📡 [SUPREME COUNCIL API] Live Socket Server Started on Port 5000")
    print(f"🌐 Engine: {current_engine.get_name()}\n")
    
    socketio.run(app, port=5000, debug=False, host='0.0.0.0')
