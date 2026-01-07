import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiSend, FiDatabase, FiTrendingUp, FiSearch, FiUser, FiCpu } from 'react-icons/fi';
import './Chat.css';

const Chat = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: 'Hello! I\'m your Lease Portfolio AI assistant. I can help you analyze your lease data, answer questions about tenants, expiration dates, rent pricing, and more. What would you like to know?',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sampleQuestions = [
    {
      icon: FiDatabase,
      question: "What is the total value of all active leases?",
      category: "Portfolio Overview"
    },
    {
      icon: FiTrendingUp,
      question: "Show me leases expiring in the next 12 months",
      category: "Expiration Analysis"
    },
    {
      icon: FiSearch,
      question: "Which tenants have the highest square footage?",
      category: "Tenant Analysis"
    }
  ];

  const handleSampleQuestion = (question) => {
    setInputValue(question);
    inputRef.current?.focus();
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
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: inputValue })
      });

      const data = await response.json();

      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: data.response || data.error || 'Sorry, I encountered an error processing your request.',
        data: data.data || null,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: 'Sorry, I\'m having trouble connecting to the backend. Please make sure the API server is running.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
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
              {messages.map((message, index) => (
                <motion.div
                  key={message.id}
                  className={`message ${message.type}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="message-avatar">
                    {message.type === 'user' ? (
                      <FiUser size={20} />
                    ) : (
                      <FiCpu size={20} />
                    )}
                  </div>
                  <div className="message-content">
                    <div className="message-header">
                      <span className="message-sender">
                        {message.type === 'user' ? 'You' : 'AI Assistant'}
                      </span>
                      <span className="message-time">
                        {formatTimestamp(message.timestamp)}
                      </span>
                    </div>
                    <div className="message-text">{message.content}</div>
                    {message.data && (
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
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </motion.div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {messages.length <= 1 && (
            <motion.div
              className="sample-questions-inline"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              <p className="sample-label">Try asking:</p>
              <div className="sample-chips">
                {sampleQuestions.map((item, index) => (
                  <button
                    key={index}
                    className="sample-chip"
                    onClick={() => handleSampleQuestion(item.question)}
                  >
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
            <p className="input-hint">
              Press Enter to send, Shift+Enter for new line
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Chat;

