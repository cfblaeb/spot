module.exports = {
	"parser": "babel-eslint",
	"parserOptions": {
		"sourceType": "module",
		"ecmaVersion": 2018,
		"ecmaFeatures": {"jsx": true, "modules": true, "experimentalObjectRestSpread": true}
	},
	"plugins": ["react"],
	"extends": ["eslint:recommended", "plugin:react/recommended",],
	"rules": {
		"comma-dangle": 0,
		"no-console": 0,
		"react/jsx-uses-vars": 1,
		"react/display-name": 1,
		"no-unused-vars": "warn",
		"no-unexpected-multiline": "warn"
	},
	"settings": {
		"react": {
			"pragma": "React",
			"version": "16.6.3"
		}
	},
	"env": {"browser": true, "es6": true},
}
