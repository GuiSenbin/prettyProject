import globals from 'globals'
import pluginJs from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'

export default [
  { ignores: ['dist/**', 'node_modules/**'] },
  {
    languageOptions: {
      globals: { ...globals.browser, ...globals.es2021 },
      ecmaVersion: 'latest',
      sourceType: 'module',
    },
    rules: {
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
      'vue/multi-word-component-names': 'off',
    },
  },
  pluginJs.configs.recommended,
  ...pluginVue.configs['flat/essential'],
]
