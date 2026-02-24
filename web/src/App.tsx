import { Header } from './components/Header';
import { CultureCard } from './components/CultureCard';
import { CultureItem } from './types/culture';
import './App.css';

// 가상 데이터 (나중에 수집 로봇의 데이터로 교체될 예정입니다.)
const MOCK_DATA: CultureItem[] = [
  {
    id: '1',
    title: '미디어 아트 전시: 서울의 빛',
    category: '전시',
    startDate: '2026-03-01',
    endDate: '2026-05-31',
    location: '서울 시립 미술관',
    imageUrl: 'https://images.unsplash.com/photo-1549490349-8643362247b5?w=400&q=80',
    isFree: true,
    target: '전 연령'
  },
  {
    id: '2',
    title: '2026 봄 클래식 콘서트',
    category: '공연',
    startDate: '2026-04-15',
    endDate: '2026-04-15',
    location: '세종문화회관',
    imageUrl: 'https://images.unsplash.com/photo-1514320291840-2e0a9bf2a9ae?w=400&q=80',
    isFree: false,
    target: '초등학생 이상'
  },
  {
    id: '3',
    title: '한강 벚꽃 축제 2026',
    category: '축제',
    startDate: '2026-04-01',
    endDate: '2026-04-10',
    location: '여의도 한강 공원',
    imageUrl: 'https://images.unsplash.com/photo-1522383225653-ed111181a951?w=400&q=80',
    isFree: true,
    target: '전 연령'
  },
  {
    id: '4',
    title: '현대 무용: 몸의 기록',
    category: '공연',
    startDate: '2026-05-10',
    endDate: '2026-05-12',
    location: '예술의 전당',
    imageUrl: 'https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=400&q=80',
    isFree: false,
    target: '중학생 이상'
  }
];

function App() {
  return (
    <div className="container">
      <Header />
      
      <main>
        <h2 className="section-title">✨ 지금 핫한 문화 정보</h2>
        
        <div className="culture-grid">
          {MOCK_DATA.map(item => (
            <CultureCard key={item.id} item={item} />
          ))}
        </div>
      </main>

      <footer style={{ textAlign: 'center', padding: '2rem', borderTop: '1px solid #334155', color: '#64748b' }}>
        <p>&copy; 2026 문화생활 통합 플랫폼 프로젝트 - 파트너님과 함께 만들어갑니다.</p>
      </footer>
    </div>
  );
}

export default App;
