import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

export default {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({
      pages: 'dist',
      assets: 'dist',
      fallback: '404.html',
      precompress: true,
      strict: true
    }),
    paths: {
      base: process.argv.includes('dev') ? '' : (process.env.BASE_PATH || '/loa-gold-calculator')
    }
  }
};
