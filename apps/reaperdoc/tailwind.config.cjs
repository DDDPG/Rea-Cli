/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['system-ui', 'sans-serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      colors: {
        reaper: {
          dark: '#1e1e1e',
          panel: '#2a2a2a',
          accent: '#00b386',
          secondary: '#4a90e2',
          warn: '#e2b340',
          danger: '#e24a4a',
        },
      },
    },
  },
  plugins: [],
};
