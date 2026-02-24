export const Header = () => {
  return (
    <header className="main-header">
      <div className="logo">🏛️ 문화생활 통합 플랫폼</div>
      <nav className="nav-menu">
        <button className="active">전체</button>
        <button>전시</button>
        <button>공연</button>
        <button>축제</button>
      </nav>
      <div className="search-bar">
        <input type="text" placeholder="문화 정보를 검색하세요..." />
      </div>
    </header>
  );
};
