import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiUploadCloud, FiCpu, FiZap, FiCheckCircle, FiClock, FiTarget, FiShield, FiTrendingUp } from 'react-icons/fi';
import './ProcessingAnimation.css';

const ProcessingAnimation = ({ stage }) => {
  const [dots, setDots] = useState('');
  const [particles, setParticles] = useState([]);

  useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => (prev.length >= 3 ? '' : prev + '.'));
    }, 500);
    return () => clearInterval(interval);
  }, []);

  // Generate neural network particles
  useEffect(() => {
    const particleArray = Array.from({ length: 25 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      delay: Math.random() * 2,
      duration: 3 + Math.random() * 2,
      size: 2 + Math.random() * 3
    }));
    setParticles(particleArray);
  }, []);

  // Color scheme: red (incomplete) -> yellow (processing) -> green (complete)
  const getStageColor = (stageId) => {
    if (stage > stageId) return '#22c55e'; // Green - complete
    if (stage === stageId) return '#f59e0b'; // Yellow/Amber - processing
    return '#FF3621'; // Red - incomplete/pending
  };

  const stages = [
    {
      id: 1,
      title: 'Uploading to Volume',
      description: 'Securely transferring document to Databricks Unity Catalog',
      icon: FiUploadCloud
    },
    {
      id: 2,
      title: 'AI Document Parser',
      description: 'Advanced ML models extracting text and structure from PDF',
      icon: FiCpu
    },
    {
      id: 3,
      title: 'Agent Extraction',
      description: 'AI agents identifying lease terms, dates, and financial details',
      icon: FiZap
    },
    {
      id: 4,
      title: 'Data Validation',
      description: 'Structuring data and preparing for your review',
      icon: FiCheckCircle
    },
    {
      id: 5,
      title: 'AI Enrichment',
      description: 'Claude AI enriching landlord & tenant financial profiles',
      icon: FiTrendingUp
    }
  ];

  return (
    <div className="processing-container">
      {/* Neural Network Background Animation */}
      <div className="neural-network-bg">
        <svg className="neural-svg" width="100%" height="100%">
          <defs>
            <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#FF3621" stopOpacity="0.6" />
              <stop offset="50%" stopColor="#FF3621" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#FF3621" stopOpacity="0.2" />
            </linearGradient>
            <filter id="glow">
              <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          
          {/* Animated connecting lines */}
          {particles.map((p1, i) => 
            particles.slice(i + 1, i + 4).map((p2, j) => (
              <motion.line
                key={`line-${i}-${j}`}
                x1={`${p1.x}%`}
                y1={`${p1.y}%`}
                x2={`${p2.x}%`}
                y2={`${p2.y}%`}
                stroke="url(#lineGradient)"
                strokeWidth="1"
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ 
                  pathLength: [0, 1, 0],
                  opacity: [0, 0.6, 0]
                }}
                transition={{
                  duration: p1.duration + p2.duration,
                  delay: p1.delay,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              />
            ))
          )}
          
          {/* Animated nodes/particles */}
          {particles.map((particle) => (
            <motion.circle
              key={particle.id}
              cx={`${particle.x}%`}
              cy={`${particle.y}%`}
              r={particle.size}
              fill="#FF3621"
              filter="url(#glow)"
              initial={{ scale: 0, opacity: 0 }}
              animate={{ 
                scale: [0, 1.5, 1],
                opacity: [0, 1, 0.7, 1],
                x: [0, Math.sin(particle.id) * 20, 0],
                y: [0, Math.cos(particle.id) * 20, 0]
              }}
              transition={{
                duration: particle.duration,
                delay: particle.delay,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            />
          ))}
        </svg>
        
        {/* Flowing data vectors */}
        {[...Array(8)].map((_, i) => (
          <motion.div
            key={`vector-${i}`}
            className="data-vector"
            style={{
              left: `${10 + i * 12}%`,
              animationDelay: `${i * 0.3}s`
            }}
            initial={{ y: '100%', opacity: 0 }}
            animate={{ 
              y: '-100%',
              opacity: [0, 1, 1, 0]
            }}
            transition={{
              duration: 4 + Math.random() * 2,
              delay: i * 0.4,
              repeat: Infinity,
              ease: "linear"
            }}
          >
            <div className="vector-bar" style={{ 
              height: `${20 + Math.random() * 40}px`,
              background: i % 2 === 0 ? '#FF3621' : 'rgba(255, 54, 33, 0.6)'
            }} />
          </motion.div>
        ))}
      </div>

      <div className="processing-header">
        <motion.div
          className="processing-spinner"
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        >
          <div className="spinner-ring"></div>
          <div className="spinner-ring-inner"></div>
        </motion.div>
        <h2 className="processing-title">Processing Your Document{dots}</h2>
        <p className="processing-subtitle">AI-powered extraction in progress</p>
      </div>

      <div className="pipeline-visualization">
        {stages.map((stageInfo, index) => {
          const IconComponent = stageInfo.icon;
          const stageColor = getStageColor(stageInfo.id);
          return (
            <motion.div
              key={stageInfo.id}
              className={`pipeline-stage ${stage >= stageInfo.id ? 'active' : ''} ${stage > stageInfo.id ? 'complete' : ''}`}
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.2 }}
            >
              <div className="stage-connector">
                {index < stages.length - 1 && (
                  <motion.div
                    className="connector-line"
                    initial={{ scaleX: 0 }}
                    animate={{ scaleX: stage > stageInfo.id ? 1 : 0 }}
                    transition={{ duration: 0.5 }}
                    style={{ backgroundColor: '#22c55e' }}
                  />
                )}
              </div>
              
              <div className="stage-content">
                <div 
                  className="stage-icon"
                  style={{ 
                    backgroundColor: `${stageColor}15`,
                    borderColor: stageColor
                  }}
                >
                  <IconComponent 
                    size={32} 
                    color={stageColor}
                  />
                </div>
                
                <div className="stage-details">
                  <h3 className="stage-title" style={{ color: stageColor }}>
                    {stageInfo.title}
                  </h3>
                  <p className="stage-description">{stageInfo.description}</p>
                  
                  {stage === stageInfo.id && (
                    <motion.div
                      className="stage-progress"
                      initial={{ width: 0 }}
                      animate={{ width: '100%' }}
                      transition={{ duration: 2, repeat: Infinity }}
                    >
                      <div className="progress-bar" style={{ backgroundColor: stageColor }}></div>
                    </motion.div>
                  )}
                  
                  {stage > stageInfo.id && (
                    <div className="stage-complete" style={{ color: stageColor }}>
                      <FiCheckCircle size={16} style={{ marginRight: '0.5rem' }} />
                      Complete
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      <div className="processing-stats">
        <div className="stat-box">
          <FiClock size={24} color="#FF3621" />
          <div className="stat-info">
            <div className="stat-label">Est. Time</div>
            <div className="stat-value">~2-3 mins</div>
          </div>
        </div>
        <div className="stat-box">
          <FiTarget size={24} color="#FF3621" />
          <div className="stat-info">
            <div className="stat-label">Accuracy</div>
            <div className="stat-value">99.2%</div>
          </div>
        </div>
        <div className="stat-box">
          <FiShield size={24} color="#FF3621" />
          <div className="stat-info">
            <div className="stat-label">Security</div>
            <div className="stat-value">Encrypted</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProcessingAnimation;

