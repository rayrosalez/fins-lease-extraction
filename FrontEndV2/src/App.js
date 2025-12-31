import React, { useState } from 'react';
import './App.css';
import Hero from './components/Hero';
import Dashboard from './components/Dashboard';

function App() {
  const [activeView, setActiveView] = useState('home');

  return (
    <div className="App">
      <nav className="navbar">
        <div className="nav-container">
          <div className="logo">
            <span className="logo-text">FINS</span>
            <span className="logo-subtext">Lease Extraction</span>
          </div>
          <div className="nav-links">
            <button 
              className={activeView === 'home' ? 'nav-link active' : 'nav-link'}
              onClick={() => setActiveView('home')}
            >
              Home
            </button>
            <button 
              className={activeView === 'dashboard' ? 'nav-link active' : 'nav-link'}
              onClick={() => setActiveView('dashboard')}
            >
              Dashboard
            </button>
            <button 
              className="cta-button"
              onClick={() => setActiveView('dashboard')}
            >
              Get Started
            </button>
          </div>
        </div>
      </nav>

      {activeView === 'home' ? (
        <Hero />
      ) : (
        <Dashboard />
      )}
    </div>
  );
}

export default App;

