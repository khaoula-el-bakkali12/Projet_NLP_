/** @type {import('tailwindcss').Config} */

// Warm "RoomVision" clay scale — reused for legacy blue/medical tokens
const clay = {
  50:  '#faf5ef',
  100: '#f2e6d8',
  200: '#e4ccb0',
  300: '#d3ad85',
  400: '#bf8b5c',
  500: '#a86f3d',
  600: '#8a4f2a',
  700: '#6f3e20',
  800: '#5a3219',
  900: '#4d2f1c',
  950: '#2c1c12',
}

export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans:    ['Inter', 'system-ui', 'sans-serif'],
        display: ['"Playfair Display"', 'Georgia', 'serif'],
        serif:   ['"Playfair Display"', 'Georgia', 'serif'],
      },
      colors: {
        clay,
        cream: {
          50:  '#fffdf9',
          100: '#f9f4ec',
          200: '#f6f1e8',
          300: '#ece3d6',
          400: '#e7ddcf',
        },
        // legacy tokens remapped to warm tones
        medical: clay,
        navy: {
          50:  '#faf5ef',
          100: '#f2e6d8',
          500: '#8a4f2a',
          700: '#2b1f15',
          900: '#241a12',
        },
        teal: {
          400: '#c0a274',
          500: '#b8824e',
        },
        // override built-in cool palettes so stray utility classes stay warm
        blue:   clay,
        sky:    clay,
        indigo: clay,
        cyan:   { 400: '#c0a274', 500: '#b8824e', 600: '#a86f3d' },
      },
      animation: {
        'fade-in':      'fadeIn 0.35s cubic-bezier(0.23,1,0.32,1) both',
        'slide-up':     'slideUp 0.35s cubic-bezier(0.23,1,0.32,1) both',
        'scale-in':     'scaleIn 0.32s cubic-bezier(0.23,1,0.32,1) both',
        'slide-in-left':'slideInLeft 0.38s cubic-bezier(0.23,1,0.32,1) both',
        'float':        'float 4.5s ease-in-out infinite',
        'glow':         'glowPulse 3s ease-in-out infinite',
        'dot':          'dotBounce 1.4s ease-in-out infinite both',
        'pulse-slow':   'pulse 3s cubic-bezier(0.4,0,0.6,1) infinite',
        'spin':         'spin 0.75s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%':   { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%':   { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%':   { opacity: '0', transform: 'scale(0.88)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        slideInLeft: {
          '0%':   { opacity: '0', transform: 'translateX(-18px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%':      { transform: 'translateY(-10px)' },
        },
        glowPulse: {
          '0%, 100%': { boxShadow: '0 0 16px rgba(138,79,42,0.26)' },
          '50%':      { boxShadow: '0 0 32px rgba(138,79,42,0.50), 0 0 60px rgba(138,79,42,0.18)' },
        },
        dotBounce: {
          '0%, 80%, 100%': { transform: 'translateY(0) scale(1)',    opacity: '0.6' },
          '40%':            { transform: 'translateY(-8px) scale(1.1)', opacity: '1' },
        },
      },
      boxShadow: {
        'blue-sm':  '0 4px 14px rgba(138,79,42,0.22)',
        'blue-md':  '0 8px 28px rgba(138,79,42,0.28)',
        'blue-lg':  '0 16px 48px rgba(138,79,42,0.32)',
        '3d-sm':    '0 2px 0 rgba(255,255,255,0.8) inset, 0 -1px 0 rgba(0,0,0,0.10) inset, 0 4px 12px rgba(63,45,28,0.10)',
        '3d-md':    '0 2px 0 rgba(255,255,255,0.7) inset, 0 -2px 0 rgba(0,0,0,0.12) inset, 0 8px 24px rgba(63,45,28,0.12)',
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.25rem',
        '4xl': '1.5rem',
      },
    },
  },
  plugins: [],
}
