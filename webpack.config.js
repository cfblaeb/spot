const path = require('path');

module.exports = {
  entry: './src/spot.js',
  output: {
    filename: 'spot.js',
    path: path.resolve(__dirname, 'dist')
  },
  mode: 'production'
};