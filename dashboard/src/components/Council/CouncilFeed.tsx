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
  const [activeAgents, setActiveAgents] = useState<string[]>([]); // [DATA REALISM] 추가
  const feedEndRef = useRef<HTMLDivElement>(null);
  const { socket } = useSocket();

  const participants = [
    { id: 'Partner', color: 'var(--partner)' },
    { id: 'main_ai', name: 'Main AI', color: 'var(--main-ai)' },
    { id: 'watcher', name: 'Watcher', color: 'var(--watcher)' },
    { id: 'guardian', name: 'Guardian', color: 'var(--guardian)' },
    { id: 'inspector', name: 'Inspector', color: 'var(--inspector)' },
    { id: 'debater', name: 'Debater', color: 'var(--debater)' },
  ];

  useEffect(() => {
    if (!socket) return;

    // [DATA REALISM] 실제 활성화된 에이전트 목록 수신
    socket.on('agent_status_update', (data: { active_agents: string[] }) => {
      setActiveAgents(data.active_agents || []);
      console.log(`[FEED STATUS] Active Agents: ${data.active_agents}`);
    });

    socket.on('new_council_msg', (msg: Message) => {
      setMessages(prev => [...prev, msg]);
    });

    socket.on('sync_history', (data: { chat: string }) => {
      if (data.chat) {
        const lines = data.chat.trim().split('\n');
        const parsed: Message[] = lines.map(line => {
          try {
            if (line.includes('**') && line.includes('**: ')) {
              const parts = line.split('**: ');
              const sender = parts[0].replace('**', '').trim();
              const content = parts[1];
              const text = content.substring(0, content.lastIndexOf(' (')) || content;
              const time = content.substring(content.lastIndexOf(' (') + 2, content.lastIndexOf(')')) || '00:00';
              return { sender, text, timestamp: time };
            }
          } catch(e) { return null; }
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
            {participants.map(p => {
              const isOnline = p.id === 'Partner' || activeAgents.includes(p.id);
              return (
                <div key={p.id} className={`participant-item-mini ${isOnline ? 'online' : 'offline'}`}>
                  <div className={`status-indicator ${isOnline ? 'active' : 'inactive'}`}></div>
                  <span className="p-name-mini" style={{ color: isOnline ? p.color : '#333' }}>
                    {isOnline ? (p.name || p.id.toUpperCase()) : '--- EMPTY ---'}
                  </span>
                </div>
              );
            })}
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
