/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontSize: {
        // Adding custom larger sizes
        '10xl': '10rem',     // 160px
        '11xl': '12rem',     // 192px
        '12xl': '14rem',     // 224px
        '13xl': '16rem',     // 256px
        'super': '20rem',    // 320px
        'mega': '25rem',     // 400px
      },
      fontFamily: {
        fredoka: ['Fredoka One', 'cursive'],
        bubblegum: ['Bubblegum Sans', 'cursive'],
        righteous: ['Righteous', 'cursive'],
        comicneue: ['Comic Neue', 'cursive'],
        doodle: ["Monoton", "serif"]
        // Add more bubble fonts as needed
      },
    },
  },
  plugins: [],
}