import { useState } from 'react';

interface SubGroup {
  title: string;
  items: string[];
}

interface MainCategory {
  name: string;
  icon: string;
  groups: SubGroup[];
}

interface Props {
  activeCategory: string;
  onCategoryChange: (category: string, subCategory?: string) => void;
}

export const Header = ({ activeCategory, onCategoryChange }: Props) => {
  const [hoveredCategory, setHoveredCategory] = useState<string | null>(null);

  const mainCategories: MainCategory[] = [
    { 
      name: '공연', 
      icon: '🎭', 
      groups: [
        { title: '연극/뮤지컬', items: ['연극', '뮤지컬', '낭독극', '대학 연극제'] },
        { title: '클래식/오페라/무용', items: ['독주회', '오케스트라', '발레', '현대무용', '오페라'] },
        { title: '국악/전통예술', items: ['판소리', '사물놀이', '전통무용', '민속 행사'] },
        { title: '대중음악', items: ['인디 밴드', '재즈', '록', '라이브 클럽'] },
        { title: '버스킹/거리공연', items: ['야외 현장 공연', '마임', '거리 퍼포먼스'] },
        { title: '아동/가족/마술', items: ['인형극', '아동/어린이 뮤지컬', '마술쇼', '구연동화'] },
        { title: '기타', items: ['낭독회', '토크 콘서트', '복합 예술'] }
      ] 
    },
    { 
      name: '영화', 
      icon: '🎬', 
      groups: [
        { title: '시사회/혜택', items: ['시사회 응모', '무대인사(무료)', '선착순 예매권', '제휴 혜택/쿠폰', '극장 이벤트'] },
        { title: '야외/자동차 상영', items: ['자동차 극장(무료)', '한강 무비나잇', '공원/숲속 상영', '옥상 영화관', '찾아가는 영화관'] },
        { title: '아동/애니메이션', items: ['어린이 전용 상영', '아동용 애니메이션', '구연동화 영화'] },
        { title: '마을/공공 상영', items: ['도서관 주말 영화', '미디어센터', '구청 강당', '주민센터 상영'] },
        { title: '영화제/이벤트 상영', items: ['국제/국내 영화제', '축제 연계 상영', '팝업 시네마', '브랜드 기획전'] },
        { title: '시네마 토크/교육', items: ['감독/배우 GV', '영화 해설/강연', '영화 제작 체험', '영상 장비 워크숍'] },
        { title: '예술/고전/특수', items: ['영상자료원(KOFA)', '독립/예술영화', '고전 복원작', '명작 기획전', '실버/배리어프리'] }
      ] 
    },
    { 
      name: '전시', 
      icon: '🖼️', 
      groups: [
        { title: '미술전시', items: ['회화', '조각', '설치미술'] },
        { title: '사진전', items: ['다큐멘터리', '예술사진'] },
        { title: '체험전시', items: ['미디어아트', '인터랙티브 아트'] },
        { title: '박람회', items: ['아트페어', '디자인페어'] }
      ] 
    },
    { 
      name: '축제', 
      icon: '🎡', 
      groups: [
        { title: '지역축제', items: ['지자체 축제', '마을 축제'] },
        { title: '문화행사', items: ['전통행사', '시즌행사'] },
        { title: '야외축제', items: ['음악축제', '밤도깨비 야시장'] }
      ] 
    },
    { 
      name: '교육', 
      icon: '🎓', 
      groups: [
        { title: '문화/예술', items: ['실기교육', '창작워크숍'] },
        { title: '인문/교양', items: ['인문학 강연', '교양 강좌'] },
        { title: '체험/워크숍', items: ['가족체험', '원데이클래스'] },
        { title: '기타', items: ['자기계발', '취미공방'] }
      ] 
    }
  ];

  return (
    <header className="main-header" onMouseLeave={() => setHoveredCategory(null)}>
      <div className="header-top">
        <div className="header-left">
          <div className="logo" onClick={() => onCategoryChange('전체')} style={{ cursor: 'pointer' }}>
            🏛️ <span>무료문화생활</span>
          </div>
          <nav className="main-gnb">
            {mainCategories.map(cat => (
              <div 
                key={cat.name} 
                className="gnb-item-wrapper"
                onMouseEnter={() => setHoveredCategory(cat.name)}
              >
                <button 
                  className={`gnb-btn ${activeCategory === cat.name ? 'active' : ''}`}
                  onClick={() => onCategoryChange(cat.name)}
                >
                  <span className="gnb-text">{cat.name}</span>
                </button>
              </div>
            ))}
          </nav>
        </div>
        
        <div className="header-right">
          <div className="search-box">
            <input type="text" placeholder="어떤 즐거움을 찾으시나요?" />
            <span className="search-icon">🔍</span>
          </div>
          <button className="icon-btn" title="알림">🔔</button>
          <button className="icon-btn" title="찜한 정보">⭐</button>
        </div>
      </div>

      {/* 고도화된 메가 메뉴 레이어 */}
      <div className={`mega-menu ${hoveredCategory ? 'show' : ''}`}>
        <div className="mega-menu-content">
          {mainCategories.find(c => c.name === hoveredCategory)?.groups.map(group => (
            <div key={group.title} className="mega-menu-column">
              <h4 className="mega-group-title">{group.title}</h4>
              <div className="mega-group-items">
                {group.items.map(item => (
                  <button 
                    key={item} 
                    className="mega-sub-item"
                    onClick={() => {
                      if (hoveredCategory) {
                        onCategoryChange(hoveredCategory, item);
                        setHoveredCategory(null);
                      }
                    }}
                  >
                    {item}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </header>
  );
};
