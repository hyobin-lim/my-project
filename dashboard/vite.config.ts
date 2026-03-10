import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// [STABLE] 복잡한 동적 포트 읽기 대신, 표준 5055 포트로 고정하여 안정성 확보
const targetPort = '5055';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 9999,
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
