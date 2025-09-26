import React, { useState, useEffect, useRef } from 'react';
import './FlightChatbot.css';

const FlightChatbot = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isReceiving, setIsReceiving] = useState(false);
  const messagesEndRef = useRef(null);

  // Backend API configuration
  const BACKEND_CHAT_URL = 'http://localhost:8000/api/gemini/chat';

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Send message to backend Gemini API
  const sendMessage = async () => {
    const messageText = inputMessage.trim();
    if (!messageText || isReceiving) return;

    // Add user message
    const userMessage = {
      id: crypto.randomUUID(),
      type: 'user',
      content: messageText,
    };

    // Add placeholder for bot response
    const botMessage = {
      id: crypto.randomUUID(),
      type: 'bot',
      content: '',
    };

    setMessages(prev => [...prev, userMessage, botMessage]);
    setInputMessage('');
    setIsReceiving(true);

    try {
      // Prepare the request payload for backend
      const requestBody = {
        message: messageText
      };

      console.log('🚀 Sending request to backend Gemini API...', BACKEND_CHAT_URL);
      
      const response = await fetch(BACKEND_CHAT_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Backend Error Response:', errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      console.log('✅ Received response from backend:', data);

      // Extract the generated text from backend response
      const generatedText = data.response || 'Sorry, I could not generate a response.';

      // Update the bot message with the complete response
      setMessages(prevMessages => {
        const newMessages = [...prevMessages];
        const lastMessage = newMessages[newMessages.length - 1];
        if (lastMessage && lastMessage.type === 'bot') {
          lastMessage.content = generatedText;
        }
        return newMessages;
      });

    } catch (error) {
      console.error('❌ Error calling backend API:', error);
      
      // Update bot message with error
      setMessages(prevMessages => {
        const newMessages = [...prevMessages];
        const lastMessage = newMessages[newMessages.length - 1];
        if (lastMessage && lastMessage.type === 'bot') {
          lastMessage.content = `**Error:** Unable to get response from AI assistant. Please check that the backend is running and try again.\n\nError details: ${error.message}`;
        }
        return newMessages;
      });
    } finally {
      setIsReceiving(false);
    }
  };

  // Handle Enter key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !isReceiving) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flight-chatbot">
      <div className="chatbot-header">
        <h3>Aviation Assistant (Gemini via Backend)</h3>
        <div className={`connection-status ${isReceiving ? 'busy' : 'idle'}`}>
          <span className="status-dot"></span>
          {isReceiving ? 'Thinking...' : 'Ready'}
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-message">
            <p>👨‍✈️ Welcome to your Aviation Weather Assistant!</p>
            <p>I have access to real-time aviation weather data:</p>
            <ul>
              <li>METAR - Current weather conditions</li>
              <li>TAF - Terminal forecasts</li>
              <li>PIREP - Pilot reports (turbulence, icing)</li>
              <li>SIGMET - Significant weather hazards</li>
              <li>AIRMET - Weather advisories</li>
            </ul>
            <p><small>� Try: "Weather at KJFK" or "Any SIGMETs active?"</small></p>
          </div>
        )}
        
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.type}-message`}>
            <div className="message-content">
              {message.content || (message.type === 'bot' && isReceiving ? '✍️ Generating response...' : '')}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask about weather, flight planning, or aviation guidance..."
          disabled={isReceiving}
        />
        <button
          onClick={sendMessage}
          disabled={isReceiving || !inputMessage.trim()}
        >
          {isReceiving ? '⏳' : 'Send'}
        </button>
      </div>
    </div>
  );
};

export default FlightChatbot;