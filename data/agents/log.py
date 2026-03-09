import socketio
import sys

sio = socketio.Client()

def send_log(text):
    try:
        sio.connect('http://localhost:5055')
        sio.emit('main_ai_log', {'log': text})
        sio.disconnect()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        send_log(sys.argv[1])
