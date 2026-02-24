export interface CultureItem {
  id: string;
  title: string;
  category: '전시' | '공연' | '축제' | '기타';
  startDate: string;
  endDate: string;
  location: string;
  imageUrl: string;
  isFree: boolean;
  target: string;
}
