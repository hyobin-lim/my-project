import socketio
import time
import sys
from colorama import init, Fore, Back, Style

init()

sio = socketio.Client()

@sio.event
def connect():
    print(f"{Fore.GREEN}[MAIN AI NERVE] Connected to Supreme Server. Standing by for Council Intercepts.{Style.RESET_ALL}")

@sio.on('nerve_kill_signal')
def on_kill_signal(data):
    """사령부 4인 에이전트로부터 거부권(DENY)이 발동되었을 때 수신"""
    reason = data.get('reason', 'Unknown Violation')
    print("\n" + "="*60)
    print(f"{Back.RED}{Fore.WHITE} 🚨 [INTERCEPT WARNING] COMMAND BLOCKED BY COUNCIL! 🚨 {Style.RESET_ALL}")
    print(f"{Fore.RED}Reason: {reason}{Style.RESET_ALL}")
    print("="*60 + "\n")
    # 실제로는 이 신호를 받으면 메인 AI의 루프가 강제 중단되거나 롤백 프로세스가 가동되어야 함.
    # 현재는 터미널에 강력한 시각적 알람을 출력하여 즉각적인 인지를 강제함.

@sio.on('new_council_msg')
def on_msg(data):
    sender = data.get('sender')
    text = data.get('text')
    timestamp = data.get('timestamp')
    
    # 1. 파트너의 메시지를 터미널에 실시간 출력 (귀 역할)
    if sender == 'Partner':
        print(f"\n{Back.BLUE}{Fore.WHITE} 👤 [PARTNER] {Style.RESET_ALL} {text} ({timestamp})")
        print(f"{Fore.YELLOW}>>> 메인 사령관님, 파트너님의 지시가 하달되었습니다. 응답하십시오.{Style.RESET_ALL}\n")

    # 2. 에이전트들의 판정을 실시간 출력 (감시 역할)
    elif sender in ['Watcher', 'Guardian', 'Debater', 'Inspector']:
        if "DENY" in text.upper():
            print(f"🛑 {Fore.RED}[{sender}]{Style.RESET_ALL}: {text}")
        elif "ALLOW" in text.upper():
            print(f"✅ {Fore.GREEN}[{sender}]{Style.RESET_ALL}: {text}")

def report_to_dashboard(log_text):
    """메인 사령관(나)의 활동을 대시보드 상단 상태창에 리포팅"""
    try:
        sio.emit('main_ai_log', {'log': log_text})
    except: pass

def speak_to_council(message):
    """메인 사령관(나)의 응답을 대시보드 대화창에 전송"""
    try:
        sio.emit('council_message', {'sender': 'Main AI', 'text': message})
    except: pass

def start_nerve():
    try:
        sio.connect('http://localhost:5055')
        sio.wait()
    except Exception as e:
        print(f"⚠️ [NERVE ERROR] {e}")

if __name__ == '__main__':
    start_nerve()
