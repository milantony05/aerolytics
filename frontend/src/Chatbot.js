import React, { useState, useEffect, useRef } from 'react';
import './Chatbot.css';

const Chatbot = () => {
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
    if (e.key === 'Enter' && !e.shiftKey && !isReceiving) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flight-chatbot">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="message bot-message">
            <div className="message-content">
              <strong>✈️ Aviation Weather Assistant</strong>
              <p>I have access to real-time aviation weather data:</p>
              <ul>
                <li><strong>METAR</strong> - Current weather conditions</li>
                <li><strong>TAF</strong> - Terminal forecasts</li>
                <li><strong>PIREP</strong> - Pilot reports</li>
                <li><strong>SIGMET</strong> - Weather hazards</li>
              </ul>
              <p><em>Try: "Weather at KJFK" or "Any SIGMETs active?"</em></p>
            </div>
          </div>
        )}
        
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.type}-message`}>
            <div className="message-content">
              {message.content || (message.type === 'bot' && isReceiving ? '✨ Generating response...' : '')}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-section">
        <div className="chat-input-container">
          <textarea
            className="chat-input"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Ask about weather..."
            disabled={isReceiving}
            rows={1}
          />
          <button
            className="send-button"
            onClick={sendMessage}
            disabled={isReceiving || !inputMessage.trim()}
          />
        </div>
      </div>
    </div>
  );
};

export default Chatbot;