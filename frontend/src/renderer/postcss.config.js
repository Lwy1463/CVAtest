// postcss.config.js
module.exports = {
  plugins: {
    'postcss-pxtorem': {
      rootValue: 16, // 1rem = 16px
      propList: ['*'] // 对所有属性进行转换
    }
  }
}
