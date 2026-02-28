import os
import json
import logging
from datetime import datetime
from abc import ABC, abstractmethod

# 로그 설정 (나중에 모니터링 에이전트가 이 로그를 읽을 수 있음)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('collector.log', encoding='utf-8')
    ]
)

class CollectorBase(ABC):
    """
    모든 데이터 수집 로봇(Collector)의 공통 표준 클래스.
    수집 -> 파싱 -> 저장의 3단계 프로세스를 강제함.
    """
    
    def __init__(self, source_name):
        self.source_name = source_name
        self.raw_store_path = os.path.join('data', 'store', 'raw', source_name)
        
        # 데이터 저장 폴더 자동 생성
        if not os.path.exists(self.raw_store_path):
            os.makedirs(self.raw_store_path)
            logging.info(f"[{source_name}] 저장 폴더 생성 완료: {self.raw_store_path}")

    @abstractmethod
    def fetch(self):
        """실제 웹사이트나 API에서 데이터를 가져오는 메서드 (자식 클래스에서 구현)"""
        pass

    @abstractmethod
    def parse(self, raw_content):
        """가져온 데이터를 항목별로 분해하는 메서드 (자식 클래스에서 구현)"""
        pass

    def save_raw(self, parsed_data):
        """
        정제 전의 원본에 가까운 데이터를 JSON 파일로 저장.
        파일 이름은 수집 시간(timestamp)을 기반으로 생성.
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.source_name}_{timestamp}.json"
        filepath = os.path.join(self.raw_store_path, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, ensure_ascii=False, indent=2)
            logging.info(f"[{self.source_name}] 원본 데이터 저장 성공: {filepath}")
            return filepath
        except Exception as e:
            logging.error(f"[{self.source_name}] 저장 실패: {str(e)}")
            return None

    def run(self):
        """수집 프로세스 전체를 실행하는 메인 메서드"""
        logging.info(f"[{self.source_name}] 수집 로봇 가동 시작...")
        
        raw_content = self.fetch()
        if not raw_content:
            logging.error(f"[{self.source_name}] 데이터 가져오기 실패.")
            return

        parsed_items = self.parse(raw_content)
        if not parsed_items:
            logging.warning(f"[{self.source_name}] 파싱된 항목이 없습니다.")
            return

        saved_path = self.save_raw(parsed_items)
        logging.info(f"[{self.source_name}] 수집 로봇 작업 완료.")
        return saved_path

if __name__ == "__main__":
    print("이 파일은 직접 실행하는 용도가 아닙니다. 수집기 구현체에서 상속받아 사용하세요.")
