/**
 * @description 하이엔드 나무 모델(L1-L6) 및 문화 데이터 인터페이스
 */

// L1: 뿌리 (Domain)
export type Domain = 'performance' | 'cinema' | 'exhibition' | 'broadcast' | 'festival' | 'education';

// 기회 등급 (Grade)
export type Grade = 'S' | 'A' | 'B' | 'C' | 'D';

export interface CategoryItem {
  id: string;
  name: string;
  level: number; // L1-L6
  children?: CategoryItem[];
  grade?: Grade;
  description?: string;
}

export interface CultureDomain {
  id: Domain;
  name: string;
  icon: string;
  trunks: CategoryItem[]; // L2: 기둥
}
