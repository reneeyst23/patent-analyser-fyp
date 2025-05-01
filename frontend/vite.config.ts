import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { viteSingleFile } from 'vite-plugin-singlefile';

export default defineConfig({
  server: {
    port: 8000,
    strictPort: true,
    host: true,
  },
  base: './',
  plugins: [
    react(),
    viteSingleFile(),
  ],
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
  build: {
    assetsInlineLimit: 100000000,
    rollupOptions: {
      output: {
        inlineDynamicImports: true,
      },
    },
  },
});

