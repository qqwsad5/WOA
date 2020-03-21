<template>
  <div class="newsbox">
    <li @click="detail()">{{title}},简介：{{abstract}}</li>
  </div>
</template>

<script>
export default {
  name: 'NewsBox',
  props: {
    title: String,
    abstract: String
  },
  methods:{
    detail(){
      this.$router.push({
      path:"/detail",
      query:{
        title:this.title
      }
      });
    }
  }
}
</script>
