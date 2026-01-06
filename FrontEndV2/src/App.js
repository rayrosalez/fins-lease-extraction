import React, { useState } from 'react';
import './App.css';
import Hero from './components/Hero';
import Portfolio from './components/Portfolio';
import Chat from './components/Chat';
import Upload from './components/Upload';

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
              className={activeView === 'portfolio' ? 'nav-link active' : 'nav-link'}
              onClick={() => setActiveView('portfolio')}
            >
              Portfolio
            </button>
            <button 
              className={activeView === 'chat' ? 'nav-link active' : 'nav-link'}
              onClick={() => setActiveView('chat')}
            >
              Chat
            </button>
            <button 
              className={activeView === 'upload' ? 'nav-link active' : 'nav-link'}
              onClick={() => setActiveView('upload')}
            >
              Upload & Validate
            </button>
          </div>
        </div>
      </nav>

      {activeView === 'home' && <Hero onNavigate={setActiveView} />}
      {activeView === 'portfolio' && <Portfolio />}
      {activeView === 'chat' && <Chat />}
      {activeView === 'upload' && <Upload />}
    </div>
  );
}

export default App;
