import os
import datetime
import json
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import eventlet

app = Flask(__name__)
app.config['SECRET_KEY'] = 'high-end-secret-key-v17'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENTS_DIR = os.path.join(BASE_DIR, "data", "agents")
LOGS_DIR = os.path.join(BASE_DIR, "data", "logs")
LIVE_CHAT_PATH = os.path.join(AGENTS_DIR, "live_chat.md")
ACTION_LOG_PATH = os.path.join(LOGS_DIR, "guardian_action.log")

def read_file_safe(path, tail=None):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                if tail: return "".join(lines[-tail:])
                return "".join(lines)
        except: return ""
    return ""

def record_chat_literal(sender, text, timestamp):
    try:
        with open(LIVE_CHAT_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n**{sender}**: {text} ({timestamp})\n")
    except: pass

@app.route('/api/chat', methods=['POST'])
def post_chat():
    data = request.json
    sender = data.get('sender', 'Unknown')
    text = data.get('text', '')
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    record_chat_literal(sender, text, timestamp)
    socketio.emit('new_council_msg', {'sender': sender, 'text': text, 'timestamp': timestamp})
    return jsonify({"status": "success"})

@app.route('/api/log', methods=['POST'])
def post_log():
    data = request.json
    log = data.get('log', '')
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    socketio.emit('new_work_log', {'log': log, 'timestamp': timestamp})
    return jsonify({"status": "success"})

# --- Socket Events ---

@socketio.on('connect')
def handle_connect():
    emit('sync_history', {
        'chat': read_file_safe(LIVE_CHAT_PATH, tail=50),
        'logs': read_file_safe(ACTION_LOG_PATH, tail=30)
    })

@socketio.on('council_message')
def handle_council(data):
    """하단 토론창 메시지 중계"""
    sender = data.get('sender', 'Partner')
    text = data.get('text', '')
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    record_chat_literal(sender, text, timestamp)
    emit('new_council_msg', {'sender': sender, 'text': text, 'timestamp': timestamp}, broadcast=True)

@socketio.on('main_ai_log')
def handle_work_log(data):
    """상단 명령창 메시지 중계 (중요: 메인 AI가 이를 듣고 작업 시작해야 함)"""
    log = data.get('log', '')
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    # 파일에도 기록
    with open(ACTION_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {log}\n")
    # 모든 클라이언트에 브로드캐스트 (에이전트들도 이를 들음)
    emit('new_work_log', {'log': log, 'timestamp': timestamp}, broadcast=True)

if __name__ == "__main__":
    print(f"📡 [SUPREME HUB V17.5] Neural Core Active on Port 5000...")
    socketio.run(app, port=5000, debug=False, host='0.0.0.0')
