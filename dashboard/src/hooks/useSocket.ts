import { useEffect, useState, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';

// Vite 환경 변수에서 포트를 가져오거나 기본값 5055 사용
const SOCKET_PORT = import.meta.env.VITE_SOCKET_PORT || '5055';
const SOCKET_URL = `http://localhost:${SOCKET_PORT}`;

export const useSocket = () => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    console.log(`[SOCKET] Connecting to Hub on Port: ${SOCKET_PORT}`);
    const newSocket = io(SOCKET_URL);
    
    newSocket.on('connect', () => {
      console.log('✅ Connected to Nerve Hub');
      setIsConnected(true);
    });
    
    newSocket.on('disconnect', () => {
      console.log('❌ Disconnected from Nerve Hub');
      setIsConnected(false);
    });
    
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
