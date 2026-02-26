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

  return (
    <header className="main-header" onMouseLeave={() => setHoveredCategory(null)}>
      <div className="header-top">
        <div className="header-left">
          <Logo onLogoClick={() => onCategoryChange('전체')} />
          <GNB 
            activeCategory={activeCategory} 
            onCategoryChange={onCategoryChange}
            onHoverCategory={setHoveredCategory}
          />
        </div>
        
        <SearchBox />
      </div>

      <MegaMenu 
        hoveredCategory={hoveredCategory}
        onCategoryChange={(cat, sub) => {
          onCategoryChange(cat, sub);
          setHoveredCategory(null);
        }}
        onMenuLeave={() => setHoveredCategory(null)}
      />
    </header>
  );
};
