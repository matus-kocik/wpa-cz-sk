module.exports = {
  content: [
    './templates/**/*.html',
    './**/templates/**/*.html',
    './static/js/**/*.js',
    './node_modules/flowbite/**/*.js',
    './**/*.py',
  ],
  theme: {
    extend: {
      scrollBehavior: {
        smooth: 'smooth',
      },
    },
  },
  plugins: [
    require('flowbite/plugin'),
  ],
}
