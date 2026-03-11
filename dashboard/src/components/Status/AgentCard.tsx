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
  const [workingStatus, setWorkingStatus] = useState('OFFLINE');

  useEffect(() => {
    if (!socket) return;

    const handleStatusUpdate = (data: { active_agents: string[], agent_statuses?: Record<string, string> }) => {
      const activeList = data.active_agents || [];
      setIsActive(activeList.includes(id));
      
      if (data.agent_statuses && data.agent_statuses[id]) {
        setWorkingStatus(data.agent_statuses[id]);
      } else if (activeList.includes(id)) {
        setWorkingStatus('STANDBY');
      } else {
        setWorkingStatus('OFFLINE');
      }
    };

    socket.on('agent_status_update', handleStatusUpdate);
    return () => { socket.off('agent_status_update', handleStatusUpdate); };
  }, [socket, id]);

  const getStatusDisplay = () => {
    if (!isActive) return { text: '연결 대기 중...', color: '#333', class: '' };
    if (workingStatus === 'WORKING') return { text: '🔥 실시간 활동 중', color: '#ff4d4d', class: 'pulse-active' };
    return { text: '💤 대기 모드 (Standby)', color: color, class: 'dimmed' };
  };

  const status = getStatusDisplay();

  const getIcon = () => {
    const iconColor = isActive ? (workingStatus === 'WORKING' ? '#ff4d4d' : color) : '#555';
    switch (id) {
      case 'watcher': return <Eye size={16} color={iconColor} />;
      case 'safety_guard': return <Shield size={16} color={iconColor} />;
      case 'planner': return <MessageSquare size={16} color={iconColor} />;
      case 'inspector': return <Search size={16} color={iconColor} />;
      default: return null;
    }
  };

  return (
    <div className={`agent-card ${isActive ? 'active-border' : 'inactive-border'} ${workingStatus === 'WORKING' ? 'working-border' : ''}`}>
      <div className="card-header-s">
        <div 
          className={`led ${isActive ? 'led-active' : 'led-offline'} ${status.class}`} 
          style={{ backgroundColor: status.color }}
        ></div>
        {getIcon()}
        <h4 style={{ color: isActive ? '#fff' : '#666' }}>{name}</h4>
      </div>
      <div className="activity-mini-log">
        <div className={`log-item-s ${workingStatus === 'WORKING' ? 'highlight' : ''}`}>
          {status.text}
        </div>
      </div>
    </div>
  );
};

export default AgentCard;
