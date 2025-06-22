import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  base: './',          //  <--  this line is the key
  plugins: [react()],
});
