import { MAIN_CATEGORIES } from '../../constants/categories';

interface Props {
  hoveredCategory: string | null;
  isMenuOpen: boolean;
  onCategoryChange: (category: string, subCategory: string) => void;
  onMenuLeave: () => void;
}

export const MegaMenu = ({ hoveredCategory, isMenuOpen, onCategoryChange, onMenuLeave }: Props) => {
  const currentCategory = MAIN_CATEGORIES.find(c => c.name === hoveredCategory);
  const showMenu = hoveredCategory || isMenuOpen;

  return (
    <div 
      className={`mega-menu ${showMenu ? 'show' : ''} ${isMenuOpen ? 'mobile' : ''}`}
      onMouseLeave={onMenuLeave}
    >
      <div className="mega-menu-content">
        {isMenuOpen ? (
          // 모바일 전용 전체 카테고리 리스트
          <div className="mobile-menu-grid">
            {MAIN_CATEGORIES.map(category => (
              <div key={category.name} className="mobile-menu-section">
                <h3 className="mobile-category-name">{category.icon} {category.name}</h3>
                <div className="mobile-sub-grid">
                  {category.groups.map(group => (
                    <div key={group.title} className="mobile-group-wrapper">
                      <span className="mobile-group-title">{group.title}</span>
                      <div className="mobile-item-list">
                        {group.items.map(item => (
                          <button 
                            key={item} 
                            className="mobile-sub-item"
                            onClick={() => onCategoryChange(category.name, item)}
                          >
                            {item}
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          // 데스크탑 호버 메가 메뉴
          currentCategory?.groups.map(group => (
            <div key={group.title} className="mega-menu-column">
              <h4 className="mega-group-title">{group.title}</h4>
              <div className="mega-group-items">
                {group.items.map(item => (
                  <button 
                    key={item} 
                    className="mega-sub-item"
                    onClick={() => onCategoryChange(hoveredCategory!, item)}
                  >
                    {item}
                  </button>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
