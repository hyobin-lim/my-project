import React from 'react';
import Header from './components/organisms/Header';
import Home from './pages/Home';
import Footer from './components/organisms/Footer';
import './App.css';

const App: React.FC = () => {
  return (
    <div className="app-wrapper">
      <Header />
      <main className="main-content">
        <Home />
      </main>
      <Footer />
    </div>
  );
};

export default App;
