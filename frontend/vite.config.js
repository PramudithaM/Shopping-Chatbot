import tailwindcss from '@tailwindcss/vite' // Tailwind plugin for Vite
import react from '@vitejs/plugin-react' // React plugin for Vite
import { defineConfig } from 'vite' // helper for the config object

export default defineConfig({
  plugins: [react(), tailwindcss()], // turn on React and Tailwind
})