import React from 'react';
import Header from './components/organisms/Header';
import Home from './pages/Home';
import './App.css';

const App: React.FC = () => {
  return (
    <div className="app-wrapper">
      <Header />
      <Home />
    </div>
  );
};

export default App;
