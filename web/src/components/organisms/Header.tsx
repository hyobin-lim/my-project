import React, { useState } from 'react';
import { ALL_CATEGORIES } from '../../constants/categories';
import { CategoryItem } from '../../types/culture';
import './Header.css';

const Header: React.FC = () => {
  const [activeL1, setActiveL1] = useState<string | null>(null);
  const [activeL3, setActiveL3] = useState<string | null>(null);

  return (
    <header className="main-header" onMouseLeave={() => { setActiveL1(null); setActiveL3(null); }}>
      <nav className="gnb">
        <div className="logo">
          <span className="logo-free">FREE</span>
          <span className="logo-ism">ISM</span>
        </div>
        <ul className="l1-list">
          {ALL_CATEGORIES.map((domain) => (
            <li 
              key={domain.id} 
              onMouseEnter={() => setActiveL1(domain.id)}
              className={activeL1 === domain.id ? 'active' : ''}
            >
              {domain.name}
            </li>
          ))}
        </ul>
      </nav>

      {/* Mega Menu Layer (L2 & L3) */}
      {activeL1 && (
        <div className="mega-menu">
          <div className="mega-menu-content">
            {ALL_CATEGORIES.find(d => d.id === activeL1)?.trunks.map((trunk) => (
              <div key={trunk.id} className="l2-block">
                <h3 className="l2-title">{trunk.name}</h3>
                <ul className="l3-list">
                  {trunk.children?.map((branch) => (
                    <li 
                      key={branch.id}
                      onMouseEnter={() => setActiveL3(branch.id)}
                      className="l3-item"
                    >
                      <span className="l3-name">{branch.name}</span>
                      
                      {/* L4 Detail Layer (Step-by-step Reveal) */}
                      {activeL3 === branch.id && branch.children && (
                        <div className="l4-layer">
                          {branch.children.map((twig) => (
                            <span key={twig.id} className="l4-tag">
                              {twig.name}
                            </span>
                          ))}
                        </div>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}
    </header>
  );
};

export default Header;
