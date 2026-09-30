/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        /* ChurnSense AI brand palette — original color system */
        brand: {
          50: "#f0f4ff",
          100: "#e0eaff",
          200: "#c7d7fe",
          300: "#a5bbfc",
          400: "#8196f8",
          500: "#6366f1", /* Primary indigo */
          600: "#4f46e5",
          700: "#4338ca",
          800: "#3730a3",
          900: "#312e81",
          950: "#1e1b4b",
        },
        accent: {
          DEFAULT: "#06b6d4", /* Cyan accent */
          light: "#67e8f9",
          dark: "#0891b2",
        },
        risk: {
          low: "#10b981",
          medium: "#f59e0b",
          high: "#ef4444",
          critical: "#7c3aed",
        },
        surface: {
          DEFAULT: "#0f0f1a",
          card: "#161625",
          border: "#2a2a45",
          hover: "#1e1e35",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains)", "monospace"],
      },
      backgroundImage: {
        "gradient-brand": "linear-gradient(135deg, #6366f1 0%, #06b6d4 100%)",
        "gradient-dark": "linear-gradient(180deg, #0f0f1a 0%, #161625 100%)",
        "gradient-card": "linear-gradient(135deg, rgba(99,102,241,0.1) 0%, rgba(6,182,212,0.05) 100%)",
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-out",
        "slide-up": "slideUp 0.4s ease-out",
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "shimmer": "shimmer 1.5s infinite",
        "glow": "glow 2s ease-in-out infinite alternate",
      },
      keyframes: {
        fadeIn: { from: { opacity: 0 }, to: { opacity: 1 } },
        slideUp: { from: { opacity: 0, transform: "translateY(12px)" }, to: { opacity: 1, transform: "translateY(0)" } },
        shimmer: { "0%": { backgroundPosition: "-200% 0" }, "100%": { backgroundPosition: "200% 0" } },
        glow: { from: { boxShadow: "0 0 5px rgba(99,102,241,0.3)" }, to: { boxShadow: "0 0 20px rgba(99,102,241,0.6)" } },
      },
      boxShadow: {
        "brand": "0 4px 24px rgba(99,102,241,0.25)",
        "card": "0 4px 24px rgba(0,0,0,0.4)",
        "glow-sm": "0 0 8px rgba(99,102,241,0.4)",
      },
      borderRadius: {
        xl: "0.75rem",
        "2xl": "1rem",
        "3xl": "1.5rem",
      },
    },
  },
  plugins: [],
};
