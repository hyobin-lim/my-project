import React from 'react';
import { Eye, Shield, MessageSquare, Search } from 'lucide-react';
import './AgentCard.css';

interface AgentCardProps {
  id: string;
  name: string;
  color: string;
}

const AgentCard: React.FC<AgentCardProps> = ({ id, name, color }) => {
  const getIcon = () => {
    switch (id) {
      case 'watcher': return <Eye size={16} color={color} />;
      case 'guardian': return <Shield size={16} color={color} />;
      case 'debater': return <MessageSquare size={16} color={color} />;
      case 'inspector': return <Search size={16} color={color} />;
      default: return null;
    }
  };

  return (
    <div className="agent-card">
      <div className="card-header-s">
        <div className="led led-active" style={{ backgroundColor: color }}></div>
        {getIcon()}
        <h4>{name}</h4>
      </div>
      <div className="activity-mini-log">
        <div className="log-item-s">활동 감시 중...</div>
      </div>
    </div>
  );
};

export default AgentCard;
