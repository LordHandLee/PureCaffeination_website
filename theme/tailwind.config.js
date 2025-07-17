// tailwind.config.js
module.exports = {
  content: ["./templates/**/*.html"],
  theme: {
    extend: {
      colors: {
        // Default / Retro Neon
        brand: {
          bg: '#000000',
          text: '#00FFF7',
          accent: '#FF00C7',
          secondary: '#FFFF00',
        },
        // Minimalist Theme
        minimalist: {
          bg: '#ffffff',
          text: '#111111',
          accent: '#0055FF',
          secondary: '#888888',
        },
        // Organic Theme
        organic: {
          bg: '#F5F5DC',
          text: '#2F4F4F',
          accent: '#4CAF50',
          secondary: '#8FBC8F',
        }
      },
      fontFamily: {
        neon: ['Orbitron', 'sans-serif'],
        minimalist: ['Helvetica Neue', 'sans-serif'],
        organic: ['Georgia', 'serif'],
      }
    },
  },
  plugins: [],
}
