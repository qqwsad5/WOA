<template>
  <div class="detailbox"  @click="show = !show">
    <el-card>
        <h4>{{title}}</h4>
        <p>{{abstract}}</p>
    </el-card>
    <el-collapse-transition>
        <div v-show="show">
            <div class="transition-box">el-collapse-transition</div>
            <div class="transition-box">el-collapse-transition</div>
        </div>
    </el-collapse-transition>
  </div>
</template>

<script>
export default {
  name: 'DetailBox',
  props: {
    title: String,
    abstract: String
  },
  data: () => ({
      show: false
    }),
  methods:{

  }
}
</script>

<style>
  .transition-box {
    margin-bottom: 10px;
    height: 100px;
    border-radius: 4px;
    background-color: #409EFF;
    text-align: center;
    color: #fff;
    padding: 40px 20px;
    box-sizing: border-box;
    margin-right: 20px;
  }
</style>
