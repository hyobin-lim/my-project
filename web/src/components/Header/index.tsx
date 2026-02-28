import { useState } from 'react';
import { Logo } from './Logo';
import { GNB } from './GNB';
import { SearchBox } from './SearchBox';
import { MegaMenu } from './MegaMenu';
import './Header.css';

interface Props {
  activeCategory: string;
  onCategoryChange: (category: string, subCategory?: string) => void;
}

export const Header = ({ activeCategory, onCategoryChange }: Props) => {
  const [hoveredCategory, setHoveredCategory] = useState<string | null>(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen);

  return (
    <header className={`main-header ${isMenuOpen ? 'menu-open' : ''}`} onMouseLeave={() => setHoveredCategory(null)}>
      <div className="header-top">
        <div className="header-left">
          <Logo onLogoClick={() => {
            onCategoryChange('전체');
            setIsMenuOpen(false);
          }} />
          <GNB 
            activeCategory={activeCategory} 
            onCategoryChange={onCategoryChange}
            onHoverCategory={setHoveredCategory}
          />
        </div>
        
        <div className="header-right">
          <SearchBox />
          <button className="menu-toggle" onClick={toggleMenu} aria-label="메뉴 열기">
            <span className="hamburger"></span>
          </button>
        </div>
      </div>

      <MegaMenu 
        hoveredCategory={hoveredCategory}
        isMenuOpen={isMenuOpen}
        onCategoryChange={(cat, sub) => {
          onCategoryChange(cat, sub);
          setHoveredCategory(null);
          setIsMenuOpen(false);
        }}
        onMenuLeave={() => setHoveredCategory(null)}
      />
    </header>
  );
};
