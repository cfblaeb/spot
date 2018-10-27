module.exports = {
    "env": { "browser": true, "es6": true },
    "plugins": ["react"],
    "extends": ["eslint:recommended","plugin:react/recommended",],
    "parserOptions": {
        "sourceType": "module",
        "ecmaVersion": 2018,
        "ecmaFeatures": { "jsx": true }
    },
    "rules": {
        "no-console": 0,
        "indent": [
            "error",
            "tab"
        ],
        "linebreak-style": [
            "error",
            "unix"
        ],
        "quotes": [
            "error",
            "single"
        ],
        "semi": [
            "error",
            "never"
        ]
    }
};
