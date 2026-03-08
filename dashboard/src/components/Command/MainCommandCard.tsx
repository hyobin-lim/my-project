import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Send } from 'lucide-react';
import { useSocket } from '../../hooks/useSocket';
import './MainCommandCard.css';

const MainCommandCard: React.FC = () => {
  const [logs, setLogs] = useState<string[]>([]);
  const [input, setInput] = useState('');
  const logEndRef = useRef<HTMLDivElement>(null);
  const lastSentMsgRef = useRef<string | null>(null); // 중복 방지용
  const { socket } = useSocket();

  useEffect(() => {
    if (!socket) return;

    socket.on('new_work_log', (data: { log: string }) => {
      // 내가 방금 보낸 것과 똑같은 메시지가 서버에서 오면 무시 (중복 방지)
      if (data.log === lastSentMsgRef.current) {
        lastSentMsgRef.current = null;
        return;
      }
      setLogs(prev => [...prev, data.log].slice(-100));
    });

    socket.on('sync_history', (data: { logs: string[] }) => {
      if (data.logs) {
        // 중복 제거 후 설정
        const uniqueLogs = Array.from(new Set(data.logs.map(l => l.trim())));
        setLogs(uniqueLogs);
      }
    });

    return () => {
      socket.off('new_work_log');
      socket.off('sync_history');
    };
  }, [socket]);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const handleExecute = () => {
    if (!input.trim() || !socket) return;
    
    const cmdLog = `>>> COMMANDER: ${input}`;
    lastSentMsgRef.current = cmdLog; // 기록해둠
    
    setLogs(prev => [...prev, cmdLog]);
    socket.emit('main_ai_log', { log: cmdLog });
    
    setInput('');
  };

  return (
    <div className="main-command-card">
      <div className="card-header">
        <div className="agent-identity">
          <div className="led led-active" style={{ backgroundColor: 'var(--main-ai)' }}></div>
          <Terminal size={18} color="var(--main-ai)" />
          <h3>MAIN AI COMMANDER</h3>
        </div>
      </div>
      
      <div className="work-log-viewer">
        {logs.map((log, i) => (
          <div key={i} className="log-line">
            <span className="log-prefix">{">"}</span> {log}
          </div>
        ))}
        {logs.length === 0 && <div className="log-placeholder">명령 대기 중...</div>}
        <div ref={logEndRef} />
      </div>

      <div className="command-input-wrapper">
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleExecute()}
          placeholder="사령관님의 직접 명령을 입력하십시오..."
        />
        <button onClick={handleExecute}>
          <Send size={16} />
        </button>
      </div>
    </div>
  );
};

export default MainCommandCard;
