/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        base: "#0B0F17",
        panel: "#111827",
        border: {
          DEFAULT: "#1F2937",
          strong: "#374151",
        },
        gold: {
          DEFAULT: "#C5A880",
          dark: "#B39369",
        },
        heading: "#F3F4F6",
        body: "#E2E8F0",
        "body-muted": "#D1D5DB",
        muted: "#9CA3AF",
      },
      backgroundImage: {
        "gold-gradient": "linear-gradient(135deg, #C5A880, #B39369)",
      },
    },
  },
  plugins: [],
};
