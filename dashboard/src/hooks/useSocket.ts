import { useEffect, useState, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';

// Vite Proxy를 활용하여 항상 대시보드 서버를 통해 허브에 접속
const SOCKET_URL = window.location.origin;

export const useSocket = () => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    console.log(`[SOCKET] Connecting via Proxy to Nerve Hub...`);
    // 프록시 설정 덕분에 별도의 포트 지정 없이 접속 가능
    const newSocket = io(SOCKET_URL, {
      transports: ['websocket', 'polling']
    });
    
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
