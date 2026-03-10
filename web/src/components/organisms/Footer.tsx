import React from 'react';
import './Footer.css';

const Footer: React.FC = () => {
  return (
    <footer className="main-footer">
      <div className="footer-credits">
        &copy; {new Date().getFullYear()} Free Culture Navigator. All rights reserved.
      </div>
    </footer>
  );
};

export default Footer;
