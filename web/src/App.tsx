import { useState } from 'react';
import { Header } from './components/Header';
import { CultureCard } from './components/CultureCard';
import { DetailModal } from './components/DetailModal';
import { SUB_FILTERS } from './constants/categories';
import type { CultureItem } from './types/culture';
import './App.css';

// 업데이트된 카테고리 체계를 반영한 가상 데이터
const MOCK_DATA: CultureItem[] = [
  {
    id: '1',
    title: '연극 <방구석 셰익스피어>',
    category: '공연',
    startDate: '2026-03-01',
    endDate: '2026-03-31',
    location: '대학로 소극장',
    imageUrl: 'https://images.unsplash.com/photo-1507676184212-d03ab07a01bf?w=400&q=80',
    costInfo: '지원금 5,000원',
    source: '서울문화포털'
  },
  {
    id: '2',
    title: '독립 영화제: 봄의 노래',
    category: '영화',
    startDate: '2026-04-15',
    endDate: '2026-04-20',
    location: '아트하우스 모모',
    imageUrl: 'https://images.unsplash.com/photo-1485846234645-a62644f84728?w=400&q=80',
    costInfo: '무료',
    source: '독립영화협회'
  },
  {
    id: '3',
    title: '2026 한강 밤도깨비 축제',
    category: '축제',
    startDate: '2026-05-01',
    endDate: '2026-10-31',
    location: '반포 한강공원',
    imageUrl: 'https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=400&q=80',
    costInfo: '무료',
    source: '서울시청'
  },
  {
    id: '4',
    title: '현대 미술 기획전: 빛의 정원',
    category: '전시',
    startDate: '2026-03-10',
    endDate: '2026-06-30',
    location: '국립현대미술관',
    imageUrl: 'https://images.unsplash.com/photo-1499781350541-7783f6c6a0c8?w=400&q=80',
    costInfo: '무료',
    source: '문화데이터광장'
  },
  {
    id: '5',
    title: '오페라 <마술피리>',
    category: '공연',
    startDate: '2026-06-05',
    endDate: '2026-06-07',
    location: '예술의 전당 오페라극장',
    imageUrl: 'https://images.unsplash.com/photo-1503095396549-80760a99c60e?w=400&q=80',
    costInfo: '무료 (사전예약)',
    source: '예술의 전당'
  }
];

function App() {
  const [activeCategory, setActiveCategory] = useState<string>('전체');
  const [activeSubFilter, setActiveSubFilter] = useState<string>('전체');
  const [selectedItem, setSelectedItem] = useState<CultureItem | null>(null);

  const filteredData = MOCK_DATA.filter(item => {
    const categoryMatch = activeCategory === '전체' || item.category === activeCategory;
    // TODO: 추후 실제 데이터 수집 시 세부 필터링 로직 구현 필요
    return categoryMatch;
  });

  return (
    <div className="container">
      <Header 
        activeCategory={activeCategory} 
        onCategoryChange={(cat, sub) => {
          setActiveCategory(cat);
          setActiveSubFilter(sub || '전체'); // 메가 메뉴에서 선택한 서브 카테고리 반영
        }} 
      />
      
      <main>
        <section className="category-section">
          {/* L2: 동적 세부 필터 영역 */}
          <div className="category-filters sub-filters">
            {SUB_FILTERS[activeCategory].map(sub => (
              <button 
                key={sub}
                className={activeSubFilter === sub ? 'active' : ''}
                onClick={() => setActiveSubFilter(sub)}
              >
                {sub}
              </button>
            ))}
          </div>
        </section>

        <h2 className="section-title">
          {activeCategory === '전체' ? '✨ 실시간 무료 문화 혜택' : `📌 ${activeCategory} 맞춤 정보`}
          <span className="total-count">({filteredData.length})</span>
        </h2>
        
        <div className="culture-grid">
          {filteredData.map(item => (
            <div key={item.id} onClick={() => setSelectedItem(item)} style={{ cursor: 'pointer' }}>
              <CultureCard item={item} />
            </div>
          ))}
        </div>
      </main>

      <DetailModal 
        item={selectedItem} 
        onClose={() => setSelectedItem(null)} 
      />

      <footer className="main-footer">
        <p>&copy; 2026 문화생활 통합 플랫폼 프로젝트 - 부담 없이 즐기는 우리들의 문화</p>
      </footer>
    </div>
  );
}

export default App;
