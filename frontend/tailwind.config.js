/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: "#1E3A8A",
          dark: "#152a63",
        },
        cream: "#FBF7F0",
        amber: {
          DEFAULT: "#D97706",
        },
      },
    },
  },
  plugins: [],
};
