import { useEffect, useState, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';

const SOCKET_URL = 'http://localhost:5000';

export const useSocket = () => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const newSocket = io(SOCKET_URL);
    
    newSocket.on('connect', () => setIsConnected(true));
    newSocket.on('disconnect', () => setIsConnected(false));
    
    setSocket(newSocket);
    
    return () => {
      newSocket.close();
    };
  }, []);

  const emitCouncilMessage = useCallback((sender: string, text: string) => {
    if (socket) {
      socket.emit('council_message', { sender, text });
    }
  }, [socket]);

  return { socket, isConnected, emitCouncilMessage };
};
