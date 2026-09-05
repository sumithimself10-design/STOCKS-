/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#040706",
        panel: "#0a0f0c",
        panelBorder: "#123021",
        matrix: "#39ff88",
        matrixDim: "#1c7a4a",
        matrixFaint: "#0d3a26",
        bullish: "#39ff88",
        bearish: "#ff3b30",
        amber: "#ffb020",
      },
      fontFamily: {
        mono: ["'Courier New'", "ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      boxShadow: {
        glow: "0 0 8px rgba(57, 255, 136, 0.35), 0 0 2px rgba(57, 255, 136, 0.6)",
        glowRed: "0 0 8px rgba(255, 59, 48, 0.35), 0 0 2px rgba(255, 59, 48, 0.6)",
      },
    },
  },
  plugins: [],
};
