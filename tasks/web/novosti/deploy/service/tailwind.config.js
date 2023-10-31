const defaultTheme = require("tailwindcss/defaultTheme");

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/views/**/*.html"],
  theme: {
    fontFamily: {
      serif: ["Cormorant Garamond", ...defaultTheme.fontFamily.serif],
    },
    extend: {},
  },
  plugins: [],
};
