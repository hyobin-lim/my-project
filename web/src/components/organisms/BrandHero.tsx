import React from 'react';
import './BrandHero.css';

const BrandHero: React.FC = () => {
  return (
    <section className="brand-hero">
      <div className="brand-hero-content">
        {/* Brand Name Title: Elevated to Primary Status */}
        <div className="brand-identity">
          <span className="brand-free">FREE</span>
          <span className="brand-ism">ISM</span>
        </div>

        {/* Hero Slogan: Scaled Up */}
        <h1 className="hero-slogan">
          <span className="hero-text">지갑은</span>
          <div className="hero-symbol-group">
            <span className="hero-bracket">[</span>
            <div className="hero-symbol-wrapper">
              <span className="hero-symbol comma">,</span>
            </div>
            <span className="hero-bracket">]</span>
          </div>
          
          <span className="hero-text gap">영감은</span>
          <div className="hero-symbol-group">
            <span className="hero-bracket">[</span>
            <div className="hero-symbol-wrapper">
              <span className="hero-symbol exclamation">!</span>
            </div>
            <span className="hero-bracket">]</span>
          </div>
        </h1>
        
        <div className="hero-divider"></div>
        <p className="hero-description">대한민국 모든 무료 문화생활을 굴절시켜 연결하는 프리즘</p>
      </div>
    </section>
  );
};

export default BrandHero;
