module.exports = {
  purge: {
    mode: 'all',
    content: [
    "../js/*.js",
    "../../templates/**/*.html",
    "../../templates/components/**/*.html",
    "../../templates/layouts/*.html",
    "../../templates/pages/**/*.html"],
    safelist: [
      'bg-gray-300',
      'bg-gray-50',
      'bg-green-100',
      'bg-red-100',
      'bg-blue-50',
      'bg-blue-50',
      'bg-skyblue',
      'bg-darker-skyblue',
      'bg-hard-blue',
      'col-start-1',
      'col-start-2',
      'col-start-3',
      'col-start-4',
      'col-start-5',
      'col-start-6',
      'col-start-7',
    ]
  },
  darkMode: "class", // false, 'media' or 'class'
  theme: {
    extend: {
      colors: {
        turqoise: "#00C4BA",
        skyblue: "#B2E1F4",
        "darker-skyblue": '#A2D3E7',
        "hard-blue": "#1786A3",   
      },
      fontFamily: {
        overpass: ["Overpass", "sans-serif"],
      },
    },
  },
  variants: {
    extend: {},
  },
  plugins: [],
};
