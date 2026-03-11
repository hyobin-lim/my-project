import React from 'react';
import MainCommandCard from '../Command/MainCommandCard';
import AgentCard from '../Status/AgentCard';
import { useSocket } from '../../hooks/useSocket';

const StatusHub: React.FC = () => {
  const { socket } = useSocket();

  const handleShutdown = async () => {
    if (window.confirm('사령부의 모든 시스템과 창을 종료하시겠습니까?\n(터미널의 제미나이 CLI는 유지됩니다.)')) {
      // 1. 소켓 신호 시도 (가장 빠른 방법)
      if (socket) {
        socket.emit('system_shutdown');
      }

      // 2. 비상용 REST API 시도 (소켓 장애 시 백업)
      try {
        await fetch('/api/shutdown', { method: 'POST' });
      } catch (e) {
        // 이미 소켓으로 종료되었거나 서버가 응답하지 않을 경우 무시
      }
    }
  };

  return (
    <div className="status-hub" style={{ position: 'relative' }}>
      {/* L-Size: Main AI (Grid 1x1 & 2x1) */}
      <div style={{ gridColumn: '1 / 2', gridRow: '1 / 3' }}>
        <MainCommandCard />
      </div>
      
      {/* S-Size: 4 Supreme Agents (V17.5 Elite) */}
      <AgentCard id="planner" name="PLANNER" color="var(--debater)" />
      <AgentCard id="watcher" name="WATCHER" color="var(--watcher)" />
      <AgentCard id="safety_guard" name="SAFETY GUARD" color="var(--guardian)" />
      <AgentCard id="inspector" name="INSPECTOR" color="var(--inspector)" />

      {/* Shutdown Button: Floating Top Right */}
      <button 
        onClick={handleShutdown}
        style={{
          position: 'absolute',
          top: '-45px',
          right: '10px',
          background: '#ff4d4d',
          color: 'white',
          border: 'none',
          padding: '8px 15px',
          borderRadius: '4px',
          cursor: 'pointer',
          fontSize: '11px',
          fontWeight: 'bold',
          boxShadow: '0 0 10px rgba(255, 77, 77, 0.3)',
          zIndex: 100
        }}
      >
        🔴 SYSTEM SHUTDOWN
      </button>
    </div>
  );
};

export default StatusHub;
