const path = require('path')

module.exports = {
	mode: 'production',
	entry: './src/index.jsx',
	output: {	filename: 'bundle.js', path: path.resolve(__dirname, 'dist')},
	module: {
		rules: [
			{
				test: /\.(js|jsx)$/,
				exclude: /(node_modules|bower_components)/,
				loader: 'babel-loader',
				options: { presets: ['@babel/env'] }},
			{
				test: /\.css$/,
				use: ['style-loader', 'css-loader']
			},
			{
				test: /\.svg$/,
				loader: 'svg-inline-loader'
			}
		]
	},
	resolve: { extensions: ['*', '.js', '.jsx'] },
	performance: { hints: false }
}
