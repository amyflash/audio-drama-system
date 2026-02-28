<template>
  <div>Loading...</div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

onMounted(() => {
  if (userStore.token) {
    router.replace('/')
  } else {
    router.replace('/login')
  }
})
</script>
