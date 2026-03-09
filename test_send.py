import socketio
import sys

sio = socketio.Client()

def test_communication():
    try:
        sio.connect('http://localhost:5050')
        print("📡 Sending restoration signal to Supreme Council...")
        sio.emit('council_message', {
            'sender': 'Main AI',
            'text': 'The communication bridge is restored. 4 agents, please confirm your status.'
        })
        # Wait a bit for agents to respond before exiting
        import time
        time.sleep(10) 
        sio.disconnect()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_communication()
