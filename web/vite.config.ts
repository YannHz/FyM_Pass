import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { prepararAplicacionInstalable } from './pwa'

export default defineConfig({ plugins: [react(), tailwindcss(), prepararAplicacionInstalable()], server: { port: 5173, strictPort: true, proxy: { '/api': process.env.FYM_API_URL || 'http://127.0.0.1:8000' } } })
