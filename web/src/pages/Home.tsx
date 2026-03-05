import React from 'react';
import './Home.css';

interface CultureItem {
  id: string;
  title: string;
  category: string;
  thumbnail: string;
  grade: 'S' | 'A' | 'B';
  tag: string;
  dDay?: string;
}

const MOCK_DATA: Record<string, CultureItem[]> = {
  popular: [
    { id: '1', title: '뮤지컬 <알라딘> 초대권 응모', category: '공연 > 뮤지컬', thumbnail: 'https://via.placeholder.com/300x400?text=Aladdin', grade: 'S', tag: '응모형 0원' },
    { id: '2', title: '서울스테이지11: 정오의 콘서트', category: '공연 > 클래식', thumbnail: 'https://via.placeholder.com/300x400?text=Classic', grade: 'A', tag: '사전예약' },
    { id: '3', title: '국립현대미술관 특별전', category: '전시 > 기획전', thumbnail: 'https://via.placeholder.com/300x400?text=Exhibition', grade: 'A', tag: '무료관람' },
  ],
  closing: [
    { id: '4', title: '연극 <오아시스> 잔여석 나눔', category: '공연 > 연극', thumbnail: 'https://via.placeholder.com/300x400?text=Theater', grade: 'B', tag: '선착순', dDay: 'D-1' },
    { id: '5', title: '한강 야외 영화 상영회', category: '영화 > 야외', thumbnail: 'https://via.placeholder.com/300x400?text=Movie', grade: 'B', tag: '자유입장', dDay: '오늘마감' },
  ],
  recommended: [
    { id: '6', title: '티니핑 캐릭터 뮤지컬', category: '공연 > 어린이', thumbnail: 'https://via.placeholder.com/300x400?text=Kids', grade: 'A', tag: '가족특화' },
    { id: '7', title: '북콘서트: 작가와의 만남', category: '교육 > 강연', thumbnail: 'https://via.placeholder.com/300x400?text=Book', grade: 'C', tag: '상시신청' },
  ]
};

const Home: React.FC = () => {
  const renderSection = (title: string, items: CultureItem[]) => (
    <section className="curation-section">
      <div className="section-header">
        <h2>{title}</h2>
        <button className="view-all">전체보기</button>
      </div>
      <div className="horizontal-scroll">
        {items.map((item) => (
          <div key={item.id} className="culture-card">
            <div className="thumbnail-wrapper">
              <img src={item.thumbnail} alt={item.title} />
              <div className={`grade-badge grade-${item.grade.toLowerCase()}`}>
                Grade {item.grade}
              </div>
              {item.dDay && <div className="d-day-badge">{item.dDay}</div>}
            </div>
            <div className="card-info">
              <span className="category-label">{item.category}</span>
              <h3 className="item-title">{item.title}</h3>
              <div className="benefit-tag">{item.tag}</div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );

  return (
    <main className="home-container">
      <div className="hero-banner">
        <h1>오늘의 무료 혜택을 놓치지 마세요</h1>
        <p>대한민국 No.1 무료 문화 내비게이터</p>
      </div>
      
      {renderSection('🔥 지금 가장 핫한 S급 기회', MOCK_DATA.popular)}
      {renderSection('⏰ 마감임박! 서두르세요', MOCK_DATA.closing)}
      {renderSection('👶 가족과 함께라면? 추천 콘텐츠', MOCK_DATA.recommended)}
    </main>
  );
};

export default Home;
