import React from 'react';
import { motion } from 'framer-motion';
import { 
  FiUploadCloud, FiCpu, FiZap, FiCheckCircle, FiBarChart2, 
  FiMessageSquare, FiShield, FiTrendingUp, FiDatabase, FiLayers, FiSearch
} from 'react-icons/fi';
import './Hero.css';

const Hero = () => {
  const pipelineStages = [
    {
      icon: FiUploadCloud,
      title: 'Upload Lease',
      description: 'Secure document upload to Databricks Unity Catalog Volume',
      color: '#FF3621'
    },
    {
      icon: FiCpu,
      title: 'AI Parser',
      description: 'Advanced ML models extract text and structure',
      color: '#8B4513'
    },
    {
      icon: FiZap,
      title: 'Agent Extraction',
      description: 'AI agents identify critical lease fields',
      color: '#FF3621'
    },
    {
      icon: FiCheckCircle,
      title: 'Human Validation',
      description: 'Review, correct, and add context',
      color: '#6B6B6B'
    },
    {
      icon: FiSearch,
      title: 'AI Enrichment',
      description: 'Claude AI enriches financial profiles',
      color: '#00A67E'
    }
  ];

  const capabilities = [
    {
      icon: FiBarChart2,
      title: 'Real-Time Dashboards',
      description: 'Live portfolio analytics with drill-down insights',
      gradient: 'from-[#FF3621] to-[#8B4513]'
    },
    {
      icon: FiMessageSquare,
      title: 'RAG Chat Interface',
      description: 'Natural language queries on your lease data',
      gradient: 'from-[#8B4513] to-[#6B6B6B]'
    },
    {
      icon: FiShield,
      title: 'Risk Models',
      description: 'AI-powered risk assessment and predictions',
      gradient: 'from-[#6B6B6B] to-[#FF3621]'
    }
  ];

  return (
    <div className="hero-new">
      {/* Main Hero Section */}
      <motion.div 
        className="hero-header"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <div className="databricks-badge">
          <FiLayers size={16} />
          <span>Powered by Databricks</span>
        </div>
        
        <h1 className="hero-title-new">
          Transform Lease Documents into
          <br />
          <span className="lava-text">Actionable Intelligence</span>
        </h1>
        
        <p className="hero-subtitle-new">
          AI-powered lease extraction platform built on Databricks Unity Catalog.
          Upload documents, extract data with 99%+ accuracy, and unlock portfolio insights in real-time.
        </p>

        <div className="hero-cta">
          <button className="cta-primary">
            <FiUploadCloud size={20} />
            Start Extracting
          </button>
          <button className="cta-secondary">
            <FiBarChart2 size={20} />
            View Dashboard
          </button>
        </div>

        <div className="platform-stats">
          <div className="stat-badge">
            <FiDatabase size={24} color="#FF3621" />
            <div>
              <div className="stat-value">Unity Catalog</div>
              <div className="stat-label">Secure Storage</div>
            </div>
          </div>
          <div className="stat-badge">
            <FiTrendingUp size={24} color="#8B4513" />
            <div>
              <div className="stat-value">99.2% Accuracy</div>
              <div className="stat-label">AI Extraction</div>
            </div>
          </div>
          <div className="stat-badge">
            <FiZap size={24} color="#6B6B6B" />
            <div>
              <div className="stat-value">~3 mins</div>
              <div className="stat-label">Processing Time</div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Pipeline Flow */}
      <motion.div 
        className="pipeline-section"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.3 }}
      >
        <h2 className="section-title-new">The Databricks-Powered Pipeline</h2>
        <p className="section-subtitle">
          From raw documents to intelligent insights in five seamless stages
        </p>

        <div className="pipeline-flow">
          {pipelineStages.map((stage, index) => {
            const IconComponent = stage.icon;
            return (
              <React.Fragment key={index}>
                <motion.div 
                  className="flow-stage"
                  initial={{ opacity: 0, scale: 0.8, y: 50 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  transition={{ 
                    duration: 0.6, 
                    delay: 0.5 + index * 0.2,
                    type: "spring",
                    stiffness: 100
                  }}
                  whileHover={{ 
                    scale: 1.05,
                    y: -10,
                    transition: { duration: 0.3 }
                  }}
                >
                  {/* Animated glow background */}
                  <motion.div 
                    className="stage-glow"
                    animate={{
                      scale: [1, 1.2, 1],
                      opacity: [0.3, 0.6, 0.3],
                    }}
                    transition={{
                      duration: 3,
                      repeat: Infinity,
                      delay: index * 0.5
                    }}
                    style={{ 
                      background: `radial-gradient(circle, ${stage.color}40, transparent)` 
                    }}
                  />
                  
                  {/* Stage card with animated border */}
                  <motion.div 
                    className="stage-card"
                    initial={{ rotateY: -90 }}
                    animate={{ rotateY: 0 }}
                    transition={{ duration: 0.6, delay: 0.7 + index * 0.2 }}
                  >
                    <div 
                      className="stage-icon-large"
                      style={{ borderColor: stage.color }}
                    >
                      {/* Animated icon background pulse */}
                      <motion.div
                        className="icon-pulse"
                        animate={{
                          scale: [1, 1.5, 1],
                          opacity: [0.5, 0, 0.5],
                        }}
                        transition={{
                          duration: 2,
                          repeat: Infinity,
                          delay: index * 0.3
                        }}
                        style={{ background: stage.color }}
                      />
                      <IconComponent size={32} color={stage.color} />
                    </div>
                    <h3 className="stage-title-new" style={{ color: stage.color }}>
                      {stage.title}
                    </h3>
                    <p className="stage-desc">{stage.description}</p>
                    <motion.div 
                      className="stage-number"
                      initial={{ scale: 0, rotate: -180 }}
                      animate={{ scale: 1, rotate: 0 }}
                      transition={{ 
                        duration: 0.5, 
                        delay: 0.9 + index * 0.2,
                        type: "spring"
                      }}
                    >
                      0{index + 1}
                    </motion.div>
                    
                    {/* Animated corner accents */}
                    <div className="corner-accent corner-tl" style={{ borderColor: stage.color }} />
                    <div className="corner-accent corner-br" style={{ borderColor: stage.color }} />
                  </motion.div>
                </motion.div>
                
                {index < pipelineStages.length - 1 && (
                  <div className="flow-connector">
                    {/* Animated data flow particles */}
                    <motion.div 
                      className="data-stream"
                      initial={{ x: -60, opacity: 0 }}
                      animate={{ x: 60, opacity: [0, 1, 1, 0] }}
                      transition={{
                        duration: 2,
                        repeat: Infinity,
                        delay: 1 + index * 0.5,
                        ease: "easeInOut"
                      }}
                    >
                      <div className="data-particle" style={{ background: stage.color }} />
                    </motion.div>
                    
                    {/* Multiple data particles at different speeds */}
                    <motion.div 
                      className="data-stream"
                      initial={{ x: -60, opacity: 0 }}
                      animate={{ x: 60, opacity: [0, 1, 1, 0] }}
                      transition={{
                        duration: 2.5,
                        repeat: Infinity,
                        delay: 1.3 + index * 0.5,
                        ease: "easeInOut"
                      }}
                    >
                      <div className="data-particle" style={{ background: pipelineStages[index + 1]?.color }} />
                    </motion.div>
                    
                    <motion.div 
                      className="data-stream"
                      initial={{ x: -60, opacity: 0 }}
                      animate={{ x: 60, opacity: [0, 1, 1, 0] }}
                      transition={{
                        duration: 1.8,
                        repeat: Infinity,
                        delay: 1.6 + index * 0.5,
                        ease: "easeInOut"
                      }}
                    >
                      <div className="data-particle small" style={{ background: stage.color }} />
                    </motion.div>
                    
                    {/* Animated arrow with glow */}
                    <motion.div 
                      className="flow-arrow"
                      initial={{ opacity: 0, scaleX: 0 }}
                      animate={{ opacity: 1, scaleX: 1 }}
                      transition={{ duration: 0.6, delay: 0.9 + index * 0.2 }}
                    >
                      <motion.div 
                        className="arrow-line"
                        animate={{
                          background: [
                            `linear-gradient(90deg, ${stage.color}80, ${stage.color}20)`,
                            `linear-gradient(90deg, ${stage.color}20, ${stage.color}80)`,
                            `linear-gradient(90deg, ${stage.color}80, ${stage.color}20)`,
                          ],
                        }}
                        transition={{
                          duration: 2,
                          repeat: Infinity,
                          delay: index * 0.3
                        }}
                      />
                      <motion.div 
                        className="arrow-head"
                        style={{ borderLeftColor: stage.color }}
                        animate={{
                          x: [0, 5, 0],
                          filter: [
                            `drop-shadow(0 0 5px ${stage.color})`,
                            `drop-shadow(0 0 10px ${stage.color})`,
                            `drop-shadow(0 0 5px ${stage.color})`,
                          ]
                        }}
                        transition={{
                          duration: 1.5,
                          repeat: Infinity,
                          delay: index * 0.3
                        }}
                      />
                    </motion.div>
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </div>
      </motion.div>

      {/* Capabilities Section */}
      <motion.div 
        className="capabilities-section"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.6 }}
      >
        <h2 className="section-title-new">Unlock Your Data's Potential</h2>
        <p className="section-subtitle">
          Validated lease data powers multiple intelligent applications
        </p>

        <div className="capabilities-grid">
          {capabilities.map((capability, index) => {
            const IconComponent = capability.icon;
            return (
              <motion.div 
                key={index}
                className="capability-card"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.8 + index * 0.15 }}
                whileHover={{ y: -10, transition: { duration: 0.3 } }}
              >
                <div className="capability-icon-wrapper">
                  <IconComponent size={40} color="#FF3621" />
                </div>
                <h3 className="capability-title">{capability.title}</h3>
                <p className="capability-description">{capability.description}</p>
                <div className="capability-glow"></div>
              </motion.div>
            );
          })}
        </div>
      </motion.div>

      {/* Technology Stack */}
      <motion.div 
        className="tech-stack-section"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.9 }}
      >
        <div className="tech-content">
          <div className="tech-left">
            <h2 className="section-title-new">Built on Enterprise-Grade Technology</h2>
            <p className="tech-description">
              Leveraging Databricks' unified data platform for secure, scalable, and intelligent lease management.
            </p>
            <ul className="tech-features">
              <li>
                <FiCheckCircle size={20} color="#FF3621" />
                <span>Unity Catalog for secure data governance</span>
              </li>
              <li>
                <FiCheckCircle size={20} color="#FF3621" />
                <span>Delta Lake for reliable data storage</span>
              </li>
              <li>
                <FiCheckCircle size={20} color="#FF3621" />
                <span>MLflow for model management</span>
              </li>
              <li>
                <FiCheckCircle size={20} color="#FF3621" />
                <span>SQL Warehouses for fast analytics</span>
              </li>
            </ul>
          </div>
          <div className="tech-right">
            <div className="tech-visual">
              <div className="tech-layer">
                <div className="layer-label">Gold Layer</div>
                <div className="layer-desc">Analytics & Intelligence</div>
              </div>
              <div className="tech-layer">
                <div className="layer-label">Silver Layer</div>
                <div className="layer-desc">Validated & Enriched</div>
              </div>
              <div className="tech-layer">
                <div className="layer-label">Bronze Layer</div>
                <div className="layer-desc">Raw Structured Data</div>
              </div>
              <div className="tech-layer">
                <div className="layer-label">Unity Catalog</div>
                <div className="layer-desc">Secure Storage</div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Hero;
