import { MAIN_CATEGORIES } from '../../constants/categories';

interface Props {
  activeCategory: string;
  onCategoryChange: (category: string) => void;
  onHoverCategory: (category: string | null) => void;
}

export const GNB = ({ activeCategory, onCategoryChange, onHoverCategory }: Props) => {
  return (
    <nav className="main-gnb">
      {MAIN_CATEGORIES.map(cat => (
        <div 
          key={cat.name} 
          className="gnb-item-wrapper"
          onMouseEnter={() => onHoverCategory(cat.name)}
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
  );
};
