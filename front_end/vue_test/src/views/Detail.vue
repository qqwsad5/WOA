<template>
  <div class="detail">
    <h1>This is a detail page</h1>
    <h1>谣言标题为：{{this.params.title}}</h1>
    <div class="timeline">
        <el-timeline>
            <el-timeline-item placement="top" v-for="index in 10" :key="index">
                <DetailBox title="更新 Github 模板" abstract="王小虎 提交于 2018/4/12 20:46"/>
            </el-timeline-item>
        </el-timeline>
    </div>
  </div>
</template>


<script>

import DetailBox from '@/components/DetailBox.vue'

export default {
  name: 'Detail',
  components: {
    DetailBox
  },
  data() {
      return {
        activities: [{
          content: '支持使用图标',
          timestamp: '2018-04-12 20:46',
          size: 'large',
          type: 'primary',
          icon: 'el-icon-more'
        }, {
          content: '支持自定义颜色',
          timestamp: '2018-04-03 20:46',
          color: '#0bbd87'
        }, {
          content: '支持自定义尺寸',
          timestamp: '2018-04-03 20:46',
          size: 'large'
        }, {
          content: '默认样式的节点',
          timestamp: '2018-04-03 20:46'
        }]
      };
    },
  computed:{
      params:function(){
          return this.$route.query;  //传入搜索参数
      }
  },
  created() {

  }
}
</script>

<style>

div.timeline
{
    margin: auto;
    margin-top: 5%;
    max-width :1080px;
}

</style>