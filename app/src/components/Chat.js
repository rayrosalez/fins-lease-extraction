import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiSend, FiDatabase, FiTrendingUp, FiSearch, FiUser, FiCpu, FiCode } from 'react-icons/fi';
import ReactMarkdown from 'react-markdown';
import './Chat.css';

const Chat = () => {
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: 'Hello! I\'m your Lease Portfolio AI assistant powered by Databricks Genie. Ask me anything about your lease data — tenants, expirations, rent, risk scores, and more.',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [streamStatus, setStreamStatus] = useState(null);
  const [streamThoughts, setStreamThoughts] = useState([]);
  const [streamSql, setStreamSql] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamStatus, streamThoughts, streamSql]);

  const sampleQuestions = [
    { icon: FiDatabase, question: "What is the total value of all active leases?", category: "Portfolio Overview" },
    { icon: FiTrendingUp, question: "Show me leases expiring in the next 12 months", category: "Expiration Analysis" },
    { icon: FiSearch, question: "Which tenants have the highest square footage?", category: "Tenant Analysis" }
  ];

  const handleSampleQuestion = (question) => {
    setInputValue(question);
    inputRef.current?.focus();
  };

  const PHASE_ICONS = {
    init: '🔍',
    analyzing: '📊',
    sql: '⚡',
    executing: '🗄️',
    processing: '⚙️',
    composing: '✍️',
    fetching: '📥',
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const queryText = inputValue;
    setInputValue('');
    setIsLoading(true);
    setStreamStatus(null);
    setStreamThoughts([]);
    setStreamSql(null);

    try {
      const response = await fetch('/api/chat/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: queryText, session_id: sessionId })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        let eventType = null;
        for (const line of lines) {
          if (line.startsWith('event: ')) {
            eventType = line.slice(7);
          } else if (line.startsWith('data: ') && eventType) {
            try {
              const payload = JSON.parse(line.slice(6));
              handleSSEEvent(eventType, payload);
            } catch (e) { /* skip parse errors */ }
            eventType = null;
          }
        }
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'assistant',
        content: 'Sorry, I\'m having trouble connecting to the backend.',
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
      setStreamStatus(null);
      setStreamThoughts([]);
      setStreamSql(null);
    }
  };

  const handleSSEEvent = (eventType, payload) => {
    switch (eventType) {
      case 'status':
        setStreamStatus({ message: payload.message, phase: payload.phase });
        break;
      case 'thought':
        setStreamThoughts(prev => {
          const exists = prev.find(t => t.type === payload.type);
          if (exists) return prev;
          return [...prev, payload];
        });
        break;
      case 'sql':
        setStreamSql(payload.query);
        break;
      case 'answer':
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          type: 'assistant',
          content: payload.response,
          data: payload.data || null,
          sql: payload.sql || null,
          timestamp: new Date()
        }]);
        break;
      case 'error':
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          type: 'assistant',
          content: `I wasn't able to answer that. ${payload.message}`,
          timestamp: new Date()
        }]);
        break;
      default:
        break;
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTimestamp = (date) => {
    return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
  };

  const THOUGHT_LABELS = {
    understanding: 'Understanding',
    data_sourcing: 'Data Sources',
    steps: 'Approach',
  };

  return (
    <div className="chat-page">
      <div className="chat-container">
        <motion.div
          className="chat-header"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <div className="chat-header-content">
            <FiCpu size={24} color="#FF3621" />
            <div>
              <h1 className="chat-title">Lease Portfolio AI Assistant</h1>
              <p className="chat-subtitle">Ask questions about your portfolio in natural language</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          className="chat-main"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="messages-container">
            <AnimatePresence>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  className={`message ${message.type}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="message-avatar">
                    {message.type === 'user' ? <FiUser size={20} /> : <FiCpu size={20} />}
                  </div>
                  <div className="message-content">
                    <div className="message-header">
                      <span className="message-sender">
                        {message.type === 'user' ? 'You' : 'AI Assistant'}
                      </span>
                      <span className="message-time">{formatTimestamp(message.timestamp)}</span>
                    </div>
                    <div className="message-text"><ReactMarkdown>{message.content}</ReactMarkdown></div>
                    {message.sql && (
                      <details className="message-sql">
                        <summary><FiCode size={14} /> View SQL</summary>
                        <pre>{message.sql}</pre>
                      </details>
                    )}
                    {message.data && Array.isArray(message.data) && message.data.length > 0 && (
                      <div className="message-data">
                        <div className="data-table-wrapper">
                          <table className="data-table">
                            <thead>
                              <tr>
                                {Object.keys(message.data[0]).map(col => (
                                  <th key={col}>{col.replace(/_/g, ' ')}</th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {message.data.slice(0, 20).map((row, i) => (
                                <tr key={i}>
                                  {Object.values(row).map((val, j) => (
                                    <td key={j}>{val != null ? String(val) : '—'}</td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                          {message.data.length > 20 && (
                            <p className="data-truncated">Showing 20 of {message.data.length} rows</p>
                          )}
                        </div>
                      </div>
                    )}
                    {message.data && !Array.isArray(message.data) && (
                      <div className="message-data">
                        <pre>{JSON.stringify(message.data, null, 2)}</pre>
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {isLoading && (
              <motion.div
                className="message assistant"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <div className="message-avatar">
                  <FiCpu size={20} />
                </div>
                <div className="message-content">
                  <div className="message-header">
                    <span className="message-sender">AI Assistant</span>
                  </div>
                  <div className="stream-progress">
                    {streamStatus && (
                      <motion.div
                        className="stream-status"
                        key={streamStatus.phase}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.3 }}
                      >
                        <span className="stream-icon">{PHASE_ICONS[streamStatus.phase] || '⏳'}</span>
                        <span className="stream-message">{streamStatus.message}</span>
                        <span className="stream-spinner" />
                      </motion.div>
                    )}

                    {streamThoughts.length > 0 && (
                      <motion.div
                        className="stream-thoughts"
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        transition={{ duration: 0.3 }}
                      >
                        {streamThoughts.map((thought, i) => (
                          <motion.div
                            key={thought.type}
                            className="stream-thought"
                            initial={{ opacity: 0, y: 5 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.3, delay: i * 0.1 }}
                          >
                            <span className="thought-label">{THOUGHT_LABELS[thought.type] || thought.type}:</span>
                            <span className="thought-content">{thought.content}</span>
                          </motion.div>
                        ))}
                      </motion.div>
                    )}

                    {streamSql && (
                      <motion.div
                        className="stream-sql"
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        transition={{ duration: 0.4 }}
                      >
                        <div className="stream-sql-header">
                          <FiCode size={14} />
                          <span>Generated SQL</span>
                        </div>
                        <pre className="stream-sql-code">{streamSql}</pre>
                      </motion.div>
                    )}

                    {!streamStatus && (
                      <div className="typing-indicator">
                        <span></span><span></span><span></span>
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {messages.length <= 1 && !isLoading && (
            <motion.div
              className="sample-questions-inline"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              <p className="sample-label">Try asking:</p>
              <div className="sample-chips">
                {sampleQuestions.map((item, index) => (
                  <button key={index} className="sample-chip" onClick={() => handleSampleQuestion(item.question)}>
                    <item.icon size={16} />
                    <span>{item.question}</span>
                  </button>
                ))}
              </div>
            </motion.div>
          )}

          <div className="chat-input-container">
            <div className="chat-input-wrapper">
              <input
                ref={inputRef}
                type="text"
                className="chat-input"
                placeholder="Ask a question about your lease portfolio..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={isLoading}
              />
              <button
                className="send-button"
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isLoading}
              >
                <FiSend size={20} />
              </button>
            </div>
            <p className="input-hint">Press Enter to send, Shift+Enter for new line</p>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Chat;
