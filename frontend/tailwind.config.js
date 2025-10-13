/** @type {import('tailwindcss').Config} */
const { theme } = require("./src/styles/theme");

export default {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "rgb(var(--color-gb) / <alpha-value>)",
        sidebar: "rgb(var(--color-sidebar) / <alpha-value>)",
        card: "rgb(var(--color-card) / <alpha-value>)",
        accent: "rgb(var(--color-accent) / <alpha-value>)",
        accentHover: "rgb(var(--color-accent-hover) / <alpha-value>)",
        textPrimary: "rgb(var(--color-text-primary) / <alpha-value>)",
        textSecondary: "rgb(var(--color-text-secondary) / <alpha-value>)",
        },
      fontFamily: {
        header: ['var(--font-header)', 'system-ui', 'sans-serif'],
        body: ['var(--font-body)', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};