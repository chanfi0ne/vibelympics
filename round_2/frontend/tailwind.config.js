// PURPOSE: Tailwind CSS configuration with custom terminal security theme colors and effects
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        void: '#050508',
        primary: '#0a0a0f',
        secondary: '#0f0f18',
        card: '#1a1a24',
        accent: {
          primary: '#00fff2',
          glow: '#00fff280',
          dim: '#00fff240'
        },
        severity: {
          critical: '#ff0040',
          high: '#ff6b00',
          medium: '#ffd000',
          low: '#00ff88',
          info: '#00b4ff'
        },
        text: {
          primary: '#e0e0e8',
          secondary: '#a0a0b0',
          dim: '#606070'
        }
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', '"Fira Code"', 'Consolas', 'monospace']
      },
      boxShadow: {
        'glow-sm': '0 0 10px rgba(0, 255, 242, 0.3)',
        'glow': '0 0 20px rgba(0, 255, 242, 0.4)',
        'glow-lg': '0 0 30px rgba(0, 255, 242, 0.5)',
        'critical': '0 0 20px rgba(255, 0, 64, 0.4)',
        'high': '0 0 20px rgba(255, 107, 0, 0.4)',
        'medium': '0 0 20px rgba(255, 208, 0, 0.4)',
        'low': '0 0 20px rgba(0, 255, 136, 0.4)',
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'scan': 'scan 4s linear infinite',
        'fadeIn': 'fadeIn 0.5s ease-in',
        'slideIn': 'slideIn 0.4s ease-out',
        'countUp': 'countUp 1s ease-out'
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': {
            boxShadow: '0 0 10px rgba(0, 255, 242, 0.3)',
            opacity: '1'
          },
          '50%': {
            boxShadow: '0 0 25px rgba(0, 255, 242, 0.6)',
            opacity: '0.9'
          }
        },
        'scan': {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' }
        },
        'fadeIn': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' }
        },
        'slideIn': {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' }
        },
        'countUp': {
          '0%': { transform: 'scale(1.2)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' }
        }
      }
    },
  },
  plugins: [],
}
