import { defineConfig } from 'unocss'

export default defineConfig({
  // ...UnoCSS options
  theme: {
    colors: {
      primary: '#2268ff'
    }
  },

  shortcuts: [
    {
      'absolute-center': 'absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2',
      'flex-center': 'flex items-center justify-center',
      'flex-end': 'flex items-center justify-end',
      'flex-start': 'flex items-center justify-start',
      'flex-between': 'flex items-center justify-between'
    }
  ]
})
