<template>
  <div class="home">
    <img alt="Vue logo" src="../assets/logo.png">
    <br/>
    <SearchBox/>
  </div>
</template>

<script>
// @ is an alias to /src
import SearchBox from '@/components/SearchBox.vue'

export default {
  name: 'Home',
  components: {
    SearchBox
  }
}
</script>
