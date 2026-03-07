import React, { useState } from 'react';
import Header from './components/organisms/Header';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import './App.css';

const App: React.FC = () => {
  const [view, setView] = useState<'home' | 'dashboard'>('dashboard');

  return (
    <div className="app-wrapper">
      <div className="system-nav">
        <button onClick={() => setView('home')} className={view === 'home' ? 'active' : ''}>SERVICE VIEW</button>
        <button onClick={() => setView('dashboard')} className={view === 'dashboard' ? 'active' : ''}>COMMAND CENTER</button>
      </div>
      {view === 'home' ? (
        <>
          <Header />
          <Home />
        </>
      ) : (
        <Dashboard />
      )}
    </div>
  );
};

export default App;
