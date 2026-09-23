/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: "#10223B",
          light: "#16304F",
          dark: "#0C1A2D",
        },
        cream: {
          DEFAULT: "#F5F1E7",
          dim: "#EDE7D8",
        },
        gold: {
          DEFAULT: "#F6C84A",
          dark: "#DDAE2E",
        },
        teal: {
          DEFAULT: "#4F8C87",
          dark: "#3D6F6B",
        },
        ink: "#142943",
        muted: "#8D9BAA",
      },
      fontFamily: {
        display: ["Space Grotesk", "system-ui", "sans-serif"],
        body: ["Inter", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "ui-monospace", "monospace"],
      },
      maxWidth: {
        content: "1320px",
      },
      backgroundImage: {
        "grid-navy":
          "linear-gradient(rgba(245,241,231,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(245,241,231,0.05) 1px, transparent 1px)",
        "grid-cream":
          "linear-gradient(rgba(20,41,67,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(20,41,67,0.06) 1px, transparent 1px)",
      },
      backgroundSize: {
        grid: "40px 40px",
      },
      keyframes: {
        scanline: {
          "0%": { transform: "translateY(0%)" },
          "100%": { transform: "translateY(100%)" },
        },
        blink: {
          "0%, 100%": { opacity: 1 },
          "50%": { opacity: 0.35 },
        },
      },
      animation: {
        scanline: "scanline 3.2s ease-in-out infinite alternate",
        blink: "blink 1.8s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
