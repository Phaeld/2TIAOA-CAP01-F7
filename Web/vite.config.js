import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig(({command}) => {
  if (command === 'build' && process.env.VERCEL && !process.env.VITE_API_URL?.startsWith('https://')) {
    throw new Error('Configure VITE_API_URL com a URL HTTPS pública do backend antes do deploy.');
  }
  return {plugins:[react()], server:{port:5173, strictPort:true, proxy:{'/api':'http://127.0.0.1:8000','/health':'http://127.0.0.1:8000'}}};
});
