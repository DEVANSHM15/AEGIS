/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#0B0F17',
        surface: {
          DEFAULT: '#131A29',
          light: '#1D263B',
          border: '#2A364F'
        },
        brand: {
          50: '#eefbfa',
          100: '#d5f6f4',
          500: '#00d2b8',
          600: '#00b39c',
          700: '#008f7d',
        }
      }
    },
  },
  plugins: [],
}
