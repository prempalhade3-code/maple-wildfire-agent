// tailwind.config.js
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      fontFamily: {
        serif: ['"Instrument Serif"', 'Georgia', 'serif'],
        sans: ['Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace']
      },
      colors: {
        "primary": "hsl(210, 100%, 55%)",
        "danger": "hsl(0, 80%, 55%)",
        "warn": "hsl(40, 90%, 50%)",
        "bg-dark": "hsl(220, 20%, 4%)",
        "bg-light": "hsl(215, 10%, 20%)"
      },
      boxShadow: {
        glass: "0 8px 32px 0 rgba(0, 0, 0, 0.4)",
        glow: "0 0 20px rgba(16, 185, 129, 0.15)",
        roseGlow: "0 0 20px rgba(244, 63, 94, 0.25)",
        indigoGlow: "0 0 25px rgba(99, 102, 241, 0.2)"
      }
    }
  },
  plugins: [require('@tailwindcss/typography')]
};
