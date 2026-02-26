export const SearchBox = () => {
  return (
    <div className="header-right">
      <div className="search-box">
        <input type="text" placeholder="어떤 즐거움을 찾으시나요?" />
        <span className="search-icon">🔍</span>
      </div>
      <button className="icon-btn" title="알림">🔔</button>
      <button className="icon-btn" title="찜한 정보">⭐</button>
    </div>
  );
};
