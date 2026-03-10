import React, { useState, useEffect } from 'react';
import { Eye, Shield, MessageSquare, Search } from 'lucide-react';
import './AgentCard.css';
import { useSocket } from '../../hooks/useSocket';

interface AgentCardProps {
  id: string;
  name: string;
  color: string;
}

const AgentCard: React.FC<AgentCardProps> = ({ id, name, color }) => {
  const { socket } = useSocket();
  const [isActive, setIsActive] = useState(false);

  useEffect(() => {
    if (!socket) return;

    // 서버로부터 실제 활성화된 에이전트 목록 수신
    const handleStatusUpdate = (data: { active_agents: string[] }) => {
      const activeList = data.active_agents || [];
      setIsActive(activeList.includes(id));
      console.log(`[STATUS] Agent ${id} active: ${activeList.includes(id)}`);
    };

    socket.on('agent_status_update', handleStatusUpdate);

    return () => {
      socket.off('agent_status_update', handleStatusUpdate);
    };
  }, [socket, id]);

  const getIcon = () => {
    switch (id) {
      case 'watcher': return <Eye size={16} color={isActive ? color : '#555'} />;
      case 'guardian': return <Shield size={16} color={isActive ? color : '#555'} />;
      case 'debater': return <MessageSquare size={16} color={isActive ? color : '#555'} />;
      case 'inspector': return <Search size={16} color={isActive ? color : '#555'} />;
      default: return null;
    }
  };

  return (
    <div className={`agent-card ${isActive ? 'active-border' : 'inactive-border'}`}>
      <div className="card-header-s">
        <div 
          className={`led ${isActive ? 'led-active' : 'led-offline'}`} 
          style={{ backgroundColor: isActive ? color : '#333' }}
        ></div>
        {getIcon()}
        <h4 style={{ color: isActive ? '#fff' : '#666' }}>{name}</h4>
      </div>
      <div className="activity-mini-log">
        <div className="log-item-s">
          {isActive ? '실시간 감시 가동 중' : '연결 대기 중...'}
        </div>
      </div>
    </div>
  );
};

export default AgentCard;
