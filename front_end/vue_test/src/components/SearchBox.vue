<template>
    <div class="searchbox">
        <input v-model="searchText"><button @click="search" class="test-one">搜索</button>
    </div>
</template>

<script>
export default {
  name: 'SearchBox',
  data: function () {
    return {
      searchText:"请输入搜索内容"
    }
  },
  methods:{
    search(){
      this.$router.push({
      path:"/search",
      query:{
        search:this.searchText
      }
      });
    }
  }
}
</script>