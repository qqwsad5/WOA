import Vue from 'vue'
import ElementUI from 'element-ui'
// import 'element-ui/lib/theme-chalk/index1.css'
import './theme/index.css'
import App from './App.vue'
import router from './router'
import store from './store'

Vue.config.productionTip = false
Vue.use(ElementUI);

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
