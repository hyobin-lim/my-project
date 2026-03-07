import React, { useState, useEffect, useRef } from 'react';
import './Dashboard.css';

interface AgentFeed {
  id: string;
  agent: string;
  message: string;
  status: 'SAFE' | 'WARN' | 'CRITICAL' | 'INFO';
  timestamp: string;
}

const Dashboard: React.FC = () => {
  const [feeds, setFeeds] = useState<AgentFeed[]>([]);
  const [task, setTask] = useState<string>('연결 중...');
  const [plan, setPlan] = useState<string>('연결 중...');
  const [chat, setChat] = useState<string>('연결 중...');
  const [inputMsg, setInputMsg] = useState<string>('');
  const chatEndRef = useRef<HTMLDivElement>(null);

  const fetchData = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/status');
      const data = await response.json();
      setTask(data.task || '미션 없음');
      setPlan(data.plan || '계획 없음');
      setChat(data.chat || '대화록 없음');
      
      const newFeeds: AgentFeed[] = (data.logs || []).map((log: string, idx: number) => ({
        id: `log-${idx}`,
        agent: log.includes('GUARDIAN') ? 'GUARDIAN' : 'SYSTEM',
        message: log,
        status: log.includes('RECOVERY') ? 'WARN' : 'SAFE',
        timestamp: new Date().toLocaleTimeString()
      }));
      setFeeds(newFeeds);
    } catch (err) {
      console.error('Command Center API Offline');
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  // 채팅 하단 스크롤 유지
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chat]);

  const handleSend = async () => {
    if (!inputMsg.trim()) return;
    try {
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: inputMsg })
      });
      if (response.ok) {
        setInputMsg('');
        fetchData(); // 전송 후 즉시 갱신
      }
    } catch (err) {
      alert('서버 연결 실패. API 서버가 켜져 있는지 확인하세요.');
    }
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div className="status-indicator">
          <span className="pulse-dot"></span>
          SYSTEM ACTIVE: COMMAND CENTER
        </div>
        <h1>AI STRATEGY COMMAND CENTER</h1>
        <div className="session-timer">SESSION: 2026-03-07</div>
      </div>

      <div className="dashboard-grid">
        <div className="grid-item mission-panel">
          <h3>[MISSION CONTROL]</h3>
          <div className="content-box">{task}</div>
          <div className="content-box plan-box">{plan}</div>
        </div>

        <div className="grid-item watcher-panel">
          <h3>👁️ WATCHER</h3>
          <div className="feed-list">
            {feeds.filter(f => f.agent === 'WATCHER').map(f => (
              <div key={f.id} className={`feed-item ${f.status.toLowerCase()}`}>
                [{f.timestamp}] {f.message}
              </div>
            ))}
            {feeds.length === 0 && <div className="feed-item info">전략 감시 중...</div>}
          </div>
        </div>

        <div className="grid-item debater-panel">
          <h3>🗣️ DEBATER</h3>
          <div className="feed-list">
            {feeds.filter(f => f.agent === 'DEBATER').map(f => (
              <div key={f.id} className={`feed-item ${f.status.toLowerCase()}`}>
                [{f.timestamp}] {f.message}
              </div>
            ))}
            {feeds.length === 0 && <div className="feed-item info">토론 준비 중...</div>}
          </div>
        </div>

        <div className="grid-item guardian-panel">
          <h3>🛡️ GUARDIAN</h3>
          <div className="feed-list">
            {feeds.filter(f => f.agent === 'GUARDIAN').map(f => (
              <div key={f.id} className={`feed-item ${f.status.toLowerCase()}`}>
                [{f.timestamp}] {f.message}
              </div>
            ))}
          </div>
        </div>

        <div className="grid-item inspector-panel">
          <h3>⚖️ INSPECTOR</h3>
          <div className="feed-list">
            {feeds.filter(f => f.agent === 'INSPECTOR').map(f => (
              <div key={f.id} className={`feed-item ${f.status.toLowerCase()}`}>
                [{f.timestamp}] {f.message}
              </div>
            ))}
          </div>
        </div>

        <div className="grid-item chat-panel full-width">
          <h3>🗨️ LIVE CONTEXT (PARTNER COMMAND INPUT)</h3>
          <div className="chat-content">
            <pre className="chat-raw">{chat}</pre>
            <div ref={chatEndRef} />
          </div>
          <div className="command-input-area">
            <input 
              type="text" 
              value={inputMsg} 
              onChange={(e) => setInputMsg(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="직접 명령을 입력하거나 에이전트들과 토론하세요..."
            />
            <button onClick={handleSend}>EXECUTE</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
