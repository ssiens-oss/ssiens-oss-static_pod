/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#0a0a0f',
        secondary: '#141420',
        tertiary: '#1e1e2e',
        accent: '#8b5cf6',
        'accent-hover': '#7c3aed',
      }
    },
  },
  plugins: [],
}
