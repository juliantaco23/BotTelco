import React, { useState } from 'react';
import axios from 'axios';
import '../styles.css';  // Asegúrate de que esta ruta sea correcta según la estructura de tu proyecto

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: 'user', content: input };
    setMessages([...messages, userMessage]);

    try {
      const response = await axios.post('http://localhost:8000/chat', {
        user_id: localStorage.getItem('username'),
        message: input,
      });

      const botMessage = { sender: 'bot', content: response.data.response };
      setMessages([...messages, userMessage, botMessage]);
    } catch (error) {
      console.error(error);
      setErrorMessage('An error occurred. Please try again later.');
    }

    setInput('');
  };

  return (
    <div className="chat-container">
      <h2>Chat</h2>
      <div className="chat-window">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            <p>{msg.content}</p>
          </div>
        ))}
      </div>
      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message"
        />
        <button onClick={handleSendMessage}>Send</button>
      </div>
      {errorMessage && <p className="error-message">{errorMessage}</p>}
    </div>
  );
};

export default Chat;
