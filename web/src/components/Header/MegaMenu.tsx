import { MAIN_CATEGORIES } from '../../constants/categories';

interface Props {
  hoveredCategory: string | null;
  onCategoryChange: (category: string, subCategory: string) => void;
  onMenuLeave: () => void;
}

export const MegaMenu = ({ hoveredCategory, onCategoryChange, onMenuLeave }: Props) => {
  const currentCategory = MAIN_CATEGORIES.find(c => c.name === hoveredCategory);

  return (
    <div 
      className={`mega-menu ${hoveredCategory ? 'show' : ''}`}
      onMouseLeave={onMenuLeave}
    >
      <div className="mega-menu-content">
        {currentCategory?.groups.map(group => (
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
        ))}
      </div>
    </div>
  );
};
