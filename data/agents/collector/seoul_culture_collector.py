import requests
import logging
from bs4 import BeautifulSoup
from collector_base import CollectorBase

class SeoulCultureCollector(CollectorBase):
    """
    서울문화포털(culture.seoul.go.kr)에서 무료 공연/전시 정보를 수집하는 로봇.
    """
    
    def __init__(self):
        super().__init__('seoul_culture')
        # 수집 대상 URL (예시: 무료 공연 리스트)
        self.target_url = "https://culture.seoul.go.kr/culture/main/main.do"

    def fetch(self):
        """실제 사이트에 접속하여 HTML 소스를 가져옵니다."""
        logging.info(f"[{self.source_name}] 사이트 접속 시도: {self.target_url}")
        try:
            response = requests.get(self.target_url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logging.error(f"[{self.source_name}] 접속 실패: {str(e)}")
            return None

    def parse(self, raw_html):
        """가져온 HTML에서 필요한 정보를 추출합니다."""
        logging.info(f"[{self.source_name}] 데이터 파싱 시작...")
        
        # 실제 데이터 파싱 로직 (BeautifulSoup 활용)
        soup = BeautifulSoup(raw_html, 'html.parser')
        
        # 가짜(Mock) 데이터 파싱 예시 - 실제 구현 시 각 사이트의 HTML 구조에 맞춰 수정 필요
        # 예: soup.select('.event-list-item') 등
        
        # 현재는 뼈대이므로 간단한 리스트로 반환
        items = [
            {
                "title": "서울 광장 무료 공연",
                "category": "공연",
                "location": "서울시청 앞 광장",
                "date": "2026-04-01 ~ 2026-04-30",
                "cost": "0원",
                "url": "https://culture.seoul.go.kr/example/1"
            },
            {
                "title": "도서관 인문학 특강",
                "category": "교육",
                "location": "서울시립도서관",
                "date": "2026-03-20",
                "cost": "무료",
                "url": "https://culture.seoul.go.kr/example/2"
            }
        ]
        
        logging.info(f"[{self.source_name}] 총 {len(items)}개의 항목을 발견했습니다.")
        return items

if __name__ == "__main__":
    # 로봇 단독 테스트 실행
    bot = SeoulCultureCollector()
    bot.run()
