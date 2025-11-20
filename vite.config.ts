import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import fs from 'fs';
import path from 'path';

export default defineConfig({
  plugins: [tailwindcss(), sveltekit()],
  server: {
    host: true,
    https: {
      key: fs.readFileSync(path.resolve('./cert.key')),
      cert: fs.readFileSync(path.resolve('./cert.crt'))
    }
  }
});
