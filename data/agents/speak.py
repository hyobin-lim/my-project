import socketio
import sys

sio = socketio.Client()

def send_message(text):
    try:
        sio.connect('http://localhost:5055')
        sio.emit('council_message', {'sender': 'Main AI', 'text': text})
        sio.disconnect()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        send_message(sys.argv[1])
