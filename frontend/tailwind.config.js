/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'attend-green': 'var(--color-attend-green)',
        'skip-red': 'var(--color-skip-red)',
        'optional-yellow': 'var(--color-optional-yellow)',
        'gray-200': 'var(--color-gray-200)'
      }
    },
  },
  plugins: [],
}
