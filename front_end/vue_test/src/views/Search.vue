<template>
  <div class="search">
    <h1>This is a search page</h1>
    <SearchBox/>
    <h1>搜索内容：
      <a v-if="this.params.search == null">无输入</a>
      <a v-else-if="this.params.search == ''">无输入</a>
      <a v-else>{{this.params.search}}</a>
    </h1>

    <!-- 简单列表显示搜到的谣言 -->
    <ul v-for="(item,index) in searchData" v-bind:key="index">
      <NewsBox v-bind:title="item.title" v-bind:abstract="item.abstract"/>
    </ul>

    <h1>{{currentTime}}</h1>
  </div>
</template>

<script>

import SearchBox from '@/components/SearchBox.vue'
import NewsBox from '@/components/NewsBox.vue'

export default {
  name: 'Search',
  components: {
    NewsBox,
    SearchBox
  },
  data: function () {
    return {
      searchData:[],
      timer: "",//定义一个定时器的变量
      currentTime: "" // 获取当前时间
    }
  },
  methods:{
    getData(){
      this.searchData = [];
      this.searchData.push({
          title:"标题1",
          abstract:"这个谣言主要描述了一个什么现象1"
        });
      this.searchData.push({
          title:"标题2",
          abstract:"这个谣言主要描述了一个什么现象2"
        });
      this.searchData.push({
          title:"标题3",
          abstract:"这个谣言主要描述了一个什么现象3"
        });
    }
  },
  computed:{
    params: function(){ //传入的搜索参数
      return this.$route.query;  //传入搜索参数
    }
  },

  created() {
    var _this = this; //声明一个变量指向Vue实例this，保证作用域一致
    _this.getData();  //更新数据
    this.timer = setInterval(function() {

      _this.getData();  //更新数据

      _this.currentTime = //修改数据date
        new Date().getFullYear() +
        "-" +
        (new Date().getMonth() + 1) +
        "-" +
        new Date().getDate() +
        " " +
        new Date().getHours() +
        ":" +
        new Date().getMinutes() +
        ":" +
        new Date().getSeconds();

      
    }, 1000);

  },
beforeDestroy() {
    if (this.timer) {
      clearInterval(this.timer); // 在Vue实例销毁前，清除我们的定时器
    }
  }
}
</script>