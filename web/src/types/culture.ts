export interface CultureItem {
  id: string;
  title: string;
  category: '공연' | '영화' | '축제' | '전시' | '기타';
  startDate: string;
  endDate: string;
  location: string;
  imageUrl: string;
  costInfo: string; // '무료' 또는 '지원금 5,000원' 등 구체적인 비용 정보
  target?: string;
  source: string; // 정보 출처 (예: 서울문화포털)
}
