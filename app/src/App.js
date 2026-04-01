import React, { useState } from 'react';
import './App.css';
import Hero from './components/Hero';
import Portfolio from './components/Portfolio';
import Chat from './components/Chat';
import Upload from './components/Upload';
import Forecasting from './components/Forecasting';
import { FiHelpCircle, FiX, FiMail } from 'react-icons/fi';

function App() {
  const [activeView, setActiveView] = useState('home');
  const [showHelpModal, setShowHelpModal] = useState(false);
  // Track background processing jobs across tab switches
  const [processingJob, setProcessingJob] = useState(null); // { fileName, filePath, startTime }

  return (
    <div className="App">
      <nav className="navbar">
        <div className="nav-container">
          <div className="logo">
            <span className="logo-text">
              <span className="logo-main">LeaseMiner</span>
            </span>
            <span className="logo-subtitle">Built by Fins DSAs</span>
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
              {processingJob && <span className="nav-processing-dot" title="Processing a document..." />}
            </button>
            <button 
              className={activeView === 'forecasting' ? 'nav-link active' : 'nav-link'}
              onClick={() => setActiveView('forecasting')}
            >
              Forecasting
            </button>
            <button 
              className="help-button"
              onClick={() => setShowHelpModal(true)}
              title="Get Help"
            >
              <FiHelpCircle size={20} />
            </button>
          </div>
        </div>
      </nav>

      {/* Help Modal */}
      {showHelpModal && (
        <div className="help-modal-overlay" onClick={() => setShowHelpModal(false)}>
          <div className="help-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="help-modal-header">
              <div className="help-modal-title">
                <FiHelpCircle size={24} color="#FF3621" />
                <h2>Need Help?</h2>
              </div>
              <button className="help-modal-close" onClick={() => setShowHelpModal(false)}>
                <FiX size={24} />
              </button>
            </div>
            <div className="help-modal-body">
              <p className="help-intro">
                For bug reports, feature requests, or technical assistance, please contact:
              </p>
              
              <div className="contact-list">
                <div className="contact-card">
                  <div className="contact-name">Ray Rosalez</div>
                  <div className="contact-role">DSA</div>
                  <a href="mailto:ray.rosalez@databricks.com" className="contact-email">
                    <FiMail size={16} />
                    ray.rosalez@databricks.com
                  </a>
                </div>
                
                <div className="contact-card">
                  <div className="contact-name">Susmit Sukthankar</div>
                  <div className="contact-role">DSA</div>
                  <a href="mailto:susmit.sukthankar@databricks.com" className="contact-email">
                    <FiMail size={16} />
                    susmit.sukthankar@databricks.com
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeView === 'home' && <Hero onNavigate={setActiveView} />}
      {activeView === 'portfolio' && <Portfolio />}
      {activeView === 'chat' && <Chat />}
      {activeView === 'upload' && <Upload processingJob={processingJob} setProcessingJob={setProcessingJob} />}
      {activeView === 'forecasting' && <Forecasting />}
    </div>
  );
}

export default App;
