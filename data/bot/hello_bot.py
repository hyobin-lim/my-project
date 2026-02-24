# 우리의 첫 번째 수집 로봇 테스트 파일
import sys

def check_environment():
    print("--- 파트너의 로봇 환경 점검 시작 ---")
    
    # 1. 파이썬 버전 출력
    print(f"1. 파이썬 버전: {sys.version}")
    
    # 2. 필수 라이브러리(requests) 확인
    try:
        import requests
        print("2. 'requests' 라이브러리: 설치됨 (인터넷 수집 준비 완료!)")
        
        # 3. 실제 연결 테스트 (구글 사이트 접속 시도)
        response = requests.get("https://www.google.com")
        if response.status_code == 200:
            print("3. 인터넷 연결 테스트: 성공! (세상과 대화할 수 있습니다.)")
            
    except ImportError:
        print("2. 'requests' 라이브러리: 미설치 (설치가 필요합니다.)")
        print("   -> 해결책: 터미널에 'pip install requests'를 입력해 보세요.")

    print("--- 점검 완료! ---")

if __name__ == "__main__":
    check_environment()
