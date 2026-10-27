import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  server: {
    // In dev, forward /api calls to the Django server.
    proxy: { '/api': 'http://localhost:8000' },
  },
})
