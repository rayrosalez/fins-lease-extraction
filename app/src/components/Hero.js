import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiUploadCloud, FiCpu, FiZap, FiCheckCircle, FiBarChart2, 
  FiMessageSquare, FiShield, FiTrendingUp, FiDatabase, FiLayers, FiSearch,
  FiFileText, FiFile, FiImage, FiX, FiRefreshCw
} from 'react-icons/fi';
import './Hero.css';
import ResetModal from './ResetModal';

const Hero = ({ onNavigate }) => {
  const [activeModal, setActiveModal] = useState(null);
  const [showResetModal, setShowResetModal] = useState(false);
  const pipelineStages = [
    {
      icon: FiUploadCloud,
      title: 'Upload Lease',
      description: 'Secure document upload to Databricks Unity Catalog Volume',
      color: '#FF3621',
      modal: 'upload'
    },
    {
      icon: FiCpu,
      title: 'AI Parser',
      description: 'Advanced ML models extract text and structure',
      color: '#FF3621',
      modal: 'parser'
    },
    {
      icon: FiZap,
      title: 'Agent Extraction',
      description: 'AI agents identify critical lease fields',
      color: '#FF3621',
      modal: 'agent'
    },
    {
      icon: FiCheckCircle,
      title: 'Human Validation',
      description: 'Review, correct, and add context',
      color: '#FF3621'
    },
    {
      icon: FiSearch,
      title: 'AI Enrichment',
      description: 'Claude AI enriches financial profiles',
      color: '#FF3621'
    }
  ];

  const extractionSchema = {
    "landlord": { "name": "string", "address": "string" },
    "tenant": { "name": "string", "address": "string", "industry_sector": "string" },
    "property_location": { "full_address": "string", "city": "string", "state": "string", "zip_code": "string" },
    "lease_details": { "commencement_date": "date", "expiration_date": "date", "term_months": "integer", "rentable_square_feet": "integer" },
    "financial_terms": { "annual_base_rent": "integer", "monthly_base_rent": "number", "base_rent_psf": "number", "annual_escalation_pct": "integer" },
    "risk_and_options": { "renewal_options": "string", "renewal_notice_days": "integer", "termination_rights": "string" }
  };

  const supportedFormats = [
    { ext: 'PDF', desc: 'Portable Document Format - Standard lease documents', icon: FiFileText, color: '#FF3621' },
    { ext: 'DOCX', desc: 'Microsoft Word - Editable lease documents', icon: FiFile, color: '#FF3621' },
    { ext: 'DOC', desc: 'Legacy Word documents', icon: FiFile, color: '#FF3621' },
    { ext: 'TXT', desc: 'Plain text files', icon: FiFileText, color: '#FF3621' },
    { ext: 'PNG', desc: 'Image scans with OCR capability', icon: FiImage, color: '#FF3621' },
    { ext: 'JPG', desc: 'JPEG image scans with OCR', icon: FiImage, color: '#FF3621' },
    { ext: 'TIFF', desc: 'High-quality scanned documents', icon: FiImage, color: '#FF3621' }
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
      {/* Subtle Demo Reset Button (top right corner) */}
      <div style={{
        position: 'fixed',
        top: '20px',
        right: '20px',
        zIndex: 9999
      }}>
        <button
          onClick={() => setShowResetModal(true)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '8px 14px',
            fontSize: '12px',
            fontWeight: '600',
            color: 'rgba(255, 255, 255, 0.7)',
            backgroundColor: 'rgba(30, 30, 30, 0.9)',
            border: '1px solid rgba(255, 54, 33, 0.3)',
            borderRadius: '6px',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
            backdropFilter: 'blur(10px)'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = 'rgba(255, 54, 33, 0.15)';
            e.currentTarget.style.borderColor = '#FF3621';
            e.currentTarget.style.color = '#FF3621';
            e.currentTarget.style.boxShadow = '0 4px 12px rgba(255, 54, 33, 0.3)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'rgba(30, 30, 30, 0.9)';
            e.currentTarget.style.borderColor = 'rgba(255, 54, 33, 0.3)';
            e.currentTarget.style.color = 'rgba(255, 255, 255, 0.7)';
            e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.3)';
          }}
          title="Reset demo data (for presenters)"
        >
          <FiRefreshCw size={14} />
          Reset Demo
        </button>
      </div>

      {/* Reset Modal */}
      <ResetModal 
        isOpen={showResetModal} 
        onClose={() => setShowResetModal(false)} 
      />

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
          <button className="cta-primary" onClick={() => onNavigate('upload')}>
            <FiUploadCloud size={20} />
            Start Extracting
          </button>
          <button className="cta-secondary" onClick={() => onNavigate('portfolio')}>
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
            <FiTrendingUp size={24} color="#FF3621" />
            <div>
              <div className="stat-value">99.2% Accuracy</div>
              <div className="stat-label">AI Extraction</div>
            </div>
          </div>
          <div className="stat-badge">
            <FiZap size={24} color="#FF3621" />
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
                  onClick={() => setActiveModal(stage.modal)}
                  style={{ cursor: 'pointer' }}
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

      {/* Modals */}
      <AnimatePresence>
        {activeModal && (
          <motion.div 
            className="modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setActiveModal(null)}
          >
            <motion.div 
              className="modal-content futuristic-modal"
              initial={{ scale: 0.8, y: 50, opacity: 0 }}
              animate={{ scale: 1, y: 0, opacity: 1 }}
              exit={{ scale: 0.8, y: 50, opacity: 0 }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              onClick={(e) => e.stopPropagation()}
            >
              <button className="modal-close" onClick={() => setActiveModal(null)}>
                <FiX size={24} />
              </button>

              <div className="modal-scroll-content">
              {activeModal === 'upload' && (
                <div className="modal-body">
                  <div className="modal-header">
                    <FiUploadCloud size={48} color="#FF3621" />
                    <h2>Document Upload System</h2>
                    <p className="modal-subtitle">Multi-format lease document ingestion</p>
                  </div>
                  
                  <div className="tech-grid">
                    <div className="tech-info-card">
                      <FiDatabase size={32} color="#FF3621" />
                      <h3>Unity Catalog Volume</h3>
                      <p>Secure storage in Databricks</p>
                    </div>
                    <div className="tech-info-card">
                      <FiShield size={32} color="#FF3621" />
                      <h3>Encrypted Transfer</h3>
                      <p>End-to-end TLS encryption</p>
                    </div>
                  </div>

                  <div className="formats-section">
                    <h3 className="formats-title">
                      <FiFileText size={24} color="#FF3621" />
                      Supported Formats
                    </h3>
                    <div className="formats-grid">
                      {supportedFormats.map((format, idx) => {
                        const IconComponent = format.icon;
                        return (
                          <motion.div 
                            key={idx}
                            className="format-card"
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: idx * 0.05 }}
                          >
                            <div className="format-icon" style={{ color: format.color }}>
                              <IconComponent size={32} />
                            </div>
                            <div className="format-info">
                              <strong className="format-ext">.{format.ext}</strong>
                              <p className="format-desc">{format.desc}</p>
                            </div>
                          </motion.div>
                        );
                      })}
                    </div>
                  </div>

                  <div className="modal-cta">
                    <button className="modal-button primary" onClick={() => {
                      setActiveModal(null);
                      onNavigate('upload');
                    }}>
                      <FiUploadCloud size={20} />
                      Start Upload
                    </button>
                  </div>
                </div>
              )}

              {activeModal === 'parser' && (
                <div className="modal-body">
                  <div className="modal-header">
                    <FiCpu size={48} color="#FF3621" />
                    <h2>AI Document Parser</h2>
                    <p className="modal-subtitle">Advanced text extraction & structuring pipeline</p>
                  </div>

                  <div className="code-showcase">
                    <div className="code-header">
                      <span className="code-label">Document Processing Pipeline</span>
                      <span className="code-lang">Python • Databricks</span>
                    </div>
                    <pre className="code-block">
{`def process_lease_document(file_path):
    """
    AI-powered lease document extraction
    Uses Databricks Foundation Models
    """
    
    # 1. Load document from Unity Catalog
    document = load_from_volume(file_path)
    
    # 2. OCR & Text Extraction
    text = extract_text_with_ocr(document)
    
    # 3. Document Structure Analysis
    structure = analyze_document_structure(text)
    
    # 4. Entity Recognition (NER)
    entities = extract_entities(text, structure)
    
    # 5. Field Classification
    fields = classify_lease_fields(entities)
    
    # 6. Write to Bronze Layer
    write_to_bronze_table(fields)
    
    return {
        "status": "success",
        "accuracy": 0.992,
        "fields_extracted": len(fields)
    }`}
                    </pre>
                  </div>

                  <div className="tech-grid">
                    <div className="tech-info-card">
                      <FiCpu size={28} color="#FF3621" />
                      <h4>ML Models</h4>
                      <p>BERT, GPT-4, Custom NER</p>
                    </div>
                    <div className="tech-info-card">
                      <FiTrendingUp size={28} color="#FF3621" />
                      <h4>99.2% Accuracy</h4>
                      <p>Validated extraction rate</p>
                    </div>
                  </div>
                </div>
              )}

              {activeModal === 'agent' && (
                <div className="modal-body">
                  <div className="modal-header">
                    <FiZap size={48} color="#FF3621" />
                    <h2>Agent Extraction Schema</h2>
                    <p className="modal-subtitle">Structured data extraction framework</p>
                  </div>

                  <div className="schema-section">
                    <h3 className="schema-title">Target Fields</h3>
                    <div className="schema-grid">
                      {Object.entries(extractionSchema).map(([key, value], idx) => (
                        <motion.div 
                          key={key}
                          className="schema-card"
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: idx * 0.08 }}
                        >
                          <div className="schema-key">{key}</div>
                          <div className="schema-fields">
                            {Object.entries(value).map(([field, type]) => (
                              <div key={field} className="schema-field">
                                <span className="field-name">{field}</span>
                                <span className="field-type">{type}</span>
                              </div>
                            ))}
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>

                  <div className="agent-stats">
                    <div className="stat-item">
                      <div className="stat-value">28</div>
                      <div className="stat-label">Total Fields</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-value">6</div>
                      <div className="stat-label">Categories</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-value">~2min</div>
                      <div className="stat-label">Avg Extract Time</div>
                    </div>
                  </div>
                </div>
              )}

              {activeModal === 'validation' && (
                <div className="modal-body">
                  <div className="modal-header">
                    <FiCheckCircle size={48} color="#FF3621" />
                    <h2>Human-in-the-Loop Validation</h2>
                    <p className="modal-subtitle">Expert review & correction workflow</p>
                  </div>

                  <div className="validation-flow">
                    <div className="flow-step">
                      <div className="step-number">1</div>
                      <div className="step-content">
                        <h4>Review Extracted Data</h4>
                        <p>AI presents extracted fields with confidence scores</p>
                      </div>
                    </div>
                    <div className="flow-arrow-down">↓</div>
                    <div className="flow-step">
                      <div className="step-number">2</div>
                      <div className="step-content">
                        <h4>Flag & Correct Errors</h4>
                        <p>Annotators fix inaccuracies and add missing data</p>
                      </div>
                    </div>
                    <div className="flow-arrow-down">↓</div>
                    <div className="flow-step">
                      <div className="step-number">3</div>
                      <div className="step-content">
                        <h4>Approve & Promote</h4>
                        <p>Validated data moves from Bronze → Silver layer</p>
                      </div>
                    </div>
                    <div className="flow-arrow-down">↓</div>
                    <div className="flow-step">
                      <div className="step-number">4</div>
                      <div className="step-content">
                        <h4>Model Improvement</h4>
                        <p>Corrections feed back into training pipeline</p>
                      </div>
                    </div>
                  </div>

                  <div className="validation-benefits">
                    <h4>Why Human Validation?</h4>
                    <ul>
                      <li>✓ Catches edge cases AI might miss</li>
                      <li>✓ Ensures legal accuracy for critical terms</li>
                      <li>✓ Adds domain expertise and context</li>
                      <li>✓ Continuously improves AI performance</li>
                    </ul>
                  </div>

                  <div className="modal-cta">
                    <button className="modal-button primary" onClick={() => {
                      setActiveModal(null);
                      onNavigate('upload');
                    }}>
                      <FiCheckCircle size={20} />
                      Go to Validation
                    </button>
                  </div>
                </div>
              )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Hero;
