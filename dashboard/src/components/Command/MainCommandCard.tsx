import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Send } from 'lucide-react';
import { useSocket } from '../../hooks/useSocket';
import './MainCommandCard.css';

const MainCommandCard: React.FC = () => {
  const [logs, setLogs] = useState<string[]>([]);
  const [input, setInput] = useState('');
  const [isActive, setIsActive] = useState(false);
  const logEndRef = useRef<HTMLDivElement>(null);
  const lastSentMsgRef = useRef<string | null>(null);
  const processedAgentsRef = useRef<Set<string>>(new Set()); // 이미 접속 메시지를 띄운 에이전트 관리
  const { socket } = useSocket();

  useEffect(() => {
    if (!socket) return;

    // [DATA REALISM] 모든 에이전트의 접속 상태를 실시간 감시하여 LED 제어
    const handleStatusUpdate = (data: { active_agents: string[] }) => {
      const activeList = data.active_agents || [];
      setIsActive(activeList.includes('main_ai'));
    };

    socket.on('agent_status_update', handleStatusUpdate);

    socket.on('new_work_log', (data: { log: string }) => {
      if (data.log === lastSentMsgRef.current) {
        lastSentMsgRef.current = null;
        return;
      }
      setLogs(prev => [...prev, data.log].slice(-100));
    });

    socket.on('sync_history', (data: { logs: string[] }) => {
      if (data.logs) {
        const uniqueLogs = Array.from(new Set(data.logs.map(l => l.trim())));
        setLogs(uniqueLogs);
      }
    });

    // 초기 접속 시 한 번 체크 요청 (서버에서 이미 던져주지만 확실히 하기 위해)
    socket.emit('request_status_sync');

    return () => {
      socket.off('agent_status_update');
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
    lastSentMsgRef.current = cmdLog;
    
    setLogs(prev => [...prev, cmdLog]);
    socket.emit('main_ai_log', { log: cmdLog });
    
    setInput('');
  };

  return (
    <div className={`main-command-card ${isActive ? 'active-border' : 'inactive-border'}`}>
      <div className="card-header">
        <div className="agent-identity">
          <div 
            className={`led ${isActive ? 'led-active' : 'led-offline'}`} 
            style={{ backgroundColor: isActive ? 'var(--main-ai)' : '#333' }}
          ></div>
          <Terminal size={18} color={isActive ? 'var(--main-ai)' : '#555'} />
          <h3 style={{ color: isActive ? '#fff' : '#666' }}>STRATEGIC LIAISON (조율자)</h3>
          {!isActive && <span className="conn-warning">PROCESS DISCONNECTED</span>}
        </div>
      </div>
      
      <div className="work-log-viewer">
        {!isActive && logs.length === 0 && (
          <div className="system-wait-overlay">
            <div className="spinner-mini"></div>
            <span>[429/ERROR] SYSTEM INITIALIZING...</span>
            <p>API 할당량 대기 또는 프로세스 연결 중</p>
          </div>
        )}
        {logs.map((log, i) => (
          <div key={i} className="log-line">
            <span className="log-prefix">{">"}</span> {log}
          </div>
        ))}
        {logs.length === 0 && isActive && <div className="log-placeholder">명령 대기 중...</div>}
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
