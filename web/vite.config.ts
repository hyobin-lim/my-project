import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// [STABLE] Supreme Council Nerve Hub (5055) 연결을 위한 프록시 설정
const targetPort = '5055';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    open: true,
    proxy: {
      '/socket.io': {
        target: `http://localhost:${targetPort}`,
        ws: true,
        changeOrigin: true,
      },
    },
  },
});
