import React, { useState, useEffect } from 'react';
import StatusHub from './components/Layout/StatusHub';
import CouncilFeed from './components/Council/CouncilFeed';
import './App.css';

const App: React.FC = () => {
  return (
    <div className="dashboard-layout">
      <header className="dashboard-header">
        <div className="system-title">
          <span className="pulse-dot"></span>
          AI SUPREME COUNCIL COMMAND CENTER V10.0
        </div>
        <div className="session-info">PORT: 9999 | SESSION: 2026-03-08</div>
      </header>
      
      <StatusHub />
      
      <div className="council-feed-container">
        <CouncilFeed />
      </div>
    </div>
  );
};

export default App;
