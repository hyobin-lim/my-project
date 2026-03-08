import React from 'react';
import MainCommandCard from '../Command/MainCommandCard';
import AgentCard from '../Status/AgentCard';

const StatusHub: React.FC = () => {
  return (
    <div className="status-hub">
      {/* L-Size: Main AI (Grid 1x1 & 2x1) */}
      <div style={{ gridColumn: '1 / 2', gridRow: '1 / 3' }}>
        <MainCommandCard />
      </div>
      
      {/* S-Size: 4 Supreme Agents */}
      <AgentCard id="watcher" name="WATCHER" color="var(--watcher)" />
      <AgentCard id="guardian" name="GUARDIAN" color="var(--guardian)" />
      <AgentCard id="debater" name="DEBATER" color="var(--debater)" />
      <AgentCard id="inspector" name="INSPECTOR" color="var(--inspector)" />
    </div>
  );
};

export default StatusHub;
