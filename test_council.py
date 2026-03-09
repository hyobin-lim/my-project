import socketio
import time

sio = socketio.Client()

@sio.on('new_council_msg')
def on_message(data):
    print(f"[{data['sender']}]: {data['text']} ({data['timestamp']})")

@sio.on('connect')
def on_connect():
    print("Connected to Supreme Council Server!")
    sio.emit('council_message', {'sender': 'Main AI', 'text': 'System Restoration Test: Are the 4 agents alive and listening?'})

sio.connect('http://localhost:5000')
time.sleep(10) # Wait for agent responses
sio.disconnect()
