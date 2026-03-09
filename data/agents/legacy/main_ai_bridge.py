import time
import os
import socketio
from colorama import Fore, Style, init

init() # 윈도우 색상 지원

class MainAIBridge:
    def __init__(self):
        self.sio = socketio.Client()
        self.setup_socket()

    def setup_socket(self):
        @self.sio.on('new_council_msg')
        def on_message(data):
            sender = data.get('sender')
            text = data.get('text', '')
            if sender == 'Partner':
                # 사령관님의 명령을 터미널에 화려하게 출력
                print(f"\n{Fore.YELLOW}[📢 DASHBOARD COMMAND RECEIVED]{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Commander:{Style.RESET_ALL} {text}")
                print(f"{Fore.GREEN}Action:{Style.RESET_ALL} 메인 AI가 해당 명령을 분석 중입니다...\n")

        @self.sio.on('new_work_log')
        def on_log(data):
            # 상단 명령창에 입력된 내용도 터미널에 출력
            log = data.get('log', '')
            if ">>> COMMANDER:" in log:
                print(f"\n{Fore.RED}[🚨 DIRECT COMMAND RECEIVED]{Style.RESET_ALL}")
                print(f"{Fore.WHITE}{log}{Style.RESET_ALL}\n")

        try:
            self.sio.connect('http://localhost:5000')
        except: pass

if __name__ == "__main__":
    bridge = MainAIBridge()
    try:
        while True: time.sleep(1)
    except: bridge.sio.disconnect()
