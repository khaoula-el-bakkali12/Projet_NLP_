/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans:    ['Inter', 'system-ui', 'sans-serif'],
        display: ['Outfit', 'system-ui', 'sans-serif'],
      },
      colors: {
        medical: {
          50:  '#eef7ff',
          100: '#d9edff',
          200: '#bbdeff',
          300: '#8dc8ff',
          400: '#57a8ff',
          500: '#2f86fd',
          600: '#1966f2',
          700: '#1250df',
          800: '#1542b4',
          900: '#173a8e',
          950: '#122457',
        },
        navy: {
          50:  '#f0f4ff',
          100: '#dce6ff',
          500: '#1A56DB',
          700: '#0A1628',
          900: '#060D1B',
        },
        teal: {
          400: '#2DD4BF',
          500: '#06B6D4',
        },
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
          '0%, 100%': { boxShadow: '0 0 16px rgba(26,86,219,0.28)' },
          '50%':      { boxShadow: '0 0 32px rgba(26,86,219,0.55), 0 0 60px rgba(26,86,219,0.18)' },
        },
        dotBounce: {
          '0%, 80%, 100%': { transform: 'translateY(0) scale(1)',    opacity: '0.6' },
          '40%':            { transform: 'translateY(-8px) scale(1.1)', opacity: '1' },
        },
      },
      boxShadow: {
        'blue-sm':  '0 4px 14px rgba(26,86,219,0.25)',
        'blue-md':  '0 8px 28px rgba(26,86,219,0.30)',
        'blue-lg':  '0 16px 48px rgba(26,86,219,0.35)',
        '3d-sm':    '0 2px 0 rgba(255,255,255,0.8) inset, 0 -1px 0 rgba(0,0,0,0.10) inset, 0 4px 12px rgba(0,0,0,0.10)',
        '3d-md':    '0 2px 0 rgba(255,255,255,0.7) inset, 0 -2px 0 rgba(0,0,0,0.12) inset, 0 8px 24px rgba(0,0,0,0.12)',
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
