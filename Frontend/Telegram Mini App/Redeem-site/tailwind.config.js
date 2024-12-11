/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        pink: {
          500: '#F87AFF',
        },
        purple: {
          500: '#FB93D0',
        },
        indigo: {
          500: '#FFDD99',
        },
      },
    },
  },
  plugins: [],
}