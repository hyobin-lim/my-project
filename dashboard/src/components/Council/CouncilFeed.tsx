import React, { useState, useEffect, useRef } from 'react';
import { Users, Send, MessageSquare, Zap } from 'lucide-react';
import { useSocket } from '../../hooks/useSocket';
import './CouncilFeed.css';

interface Message {
  sender: string;
  text: string;
  timestamp: string;
}

const CouncilFeed: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const feedEndRef = useRef<HTMLDivElement>(null);
  const { socket } = useSocket();

  const participants = [
    { id: 'Partner', color: 'var(--partner)' },
    { id: 'MainAI', color: 'var(--main-ai)' },
    { id: 'Watcher', color: 'var(--watcher)' },
    { id: 'Guardian', color: 'var(--guardian)' },
    { id: 'Inspector', color: 'var(--inspector)' },
    { id: 'Debater', color: 'var(--debater)' },
  ];

  useEffect(() => {
    if (!socket) return;

    socket.on('new_council_msg', (msg: Message) => {
      setMessages(prev => [...prev, msg]);
    });

    socket.on('sync_history', (data: { chat: string }) => {
      if (data.chat) {
        // [V19.0 고밀도 파싱] live_chat.md의 모든 형식을 수용하도록 개선
        const lines = data.chat.trim().split('\n');
        const parsed: Message[] = lines.map(line => {
          if (!line.includes('**')) return null;
          try {
            const senderPart = line.split('**')[1];
            const textAndTime = line.split('**: ')[1];
            if (senderPart && textAndTime) {
              const text = textAndTime.substring(0, textAndTime.lastIndexOf(' ('));
              const time = textAndTime.substring(textAndTime.lastIndexOf(' (') + 2, textAndTime.lastIndexOf(')'));
              return { sender: senderPart, text: text || textAndTime, timestamp: time || '00:00' };
            }
          } catch(e) {}
          return null;
        }).filter(m => m !== null) as Message[];
        setMessages(parsed);
      }
    });

    return () => {
      socket.off('new_council_msg');
      socket.off('sync_history');
    };
  }, [socket]);

  useEffect(() => {
    feedEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = () => {
    if (!inputText.trim() || !socket) return;
    socket.emit('council_message', { sender: 'Partner', text: inputText });
    setInputText('');
  };

  const getSenderColor = (sender: string) => {
    const p = participants.find(p => p.id.toLowerCase() === sender.toLowerCase());
    return p ? p.color : '#fff';
  };

  return (
    <div className="council-layout">
      <div className="chat-section">
        <div className="feed-header">
          <MessageSquare size={18} color="var(--debater)" />
          <h3>SUPREME COUNCIL STRATEGIC DEBATE</h3>
        </div>
        <div className="messages-area">
          {messages.map((msg, i) => (
            <div key={i} className="message-block">
              <div className="message-meta">
                <span className="sender-tag" style={{ color: getSenderColor(msg.sender) }}>
                  {msg.sender.toUpperCase()}
                </span>
                <span className="msg-time">{msg.timestamp}</span>
              </div>
              <div className="message-text">{msg.text}</div>
            </div>
          ))}
          <div ref={feedEndRef} />
        </div>
      </div>

      <div className="side-section">
        <div className="participants-panel">
          <div className="panel-header">COUNCIL MEMBERS</div>
          <div className="participants-grid">
            {participants.map(p => (
              <div key={p.id} className="participant-item-mini">
                <div className="status-indicator active"></div>
                <span className="p-name-mini" style={{ color: p.color }}>{p.id.toUpperCase()}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="input-panel">
          <div className="panel-header">DEBATE INPUT</div>
          <div className="chat-input-wrapper">
            <textarea 
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSendMessage())}
              placeholder="토론에 참여하십시오..."
            />
            <button className="send-btn" onClick={handleSendMessage}>
              <Send size={18} />
              <span>SEND TO COUNCIL</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CouncilFeed;
