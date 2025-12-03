<template>
  <v-app>
    <router-view />
    <LoginDialog v-model="showLoginDialog"/>
  </v-app>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import LoginDialog from './components/LoginDialog.vue';

const authStore = useAuthStore()

const router = useRouter()

const showLoginDialog = ref(false)

onMounted(() => {
  window.addEventListener('need-login', () => {
    showLoginDialog.value = true
  })
})

const user = JSON.parse(localStorage.getItem("user"));
if (user) {
  authStore.setUserInfo(user.email, user.password, user.name, user.surname, user.imgUrl); 
}
else {
  authStore.setUserInfo(null, null, null, null, null);
  authStore.setTokens(null, null);
  router.push('/loginpage');
}

const access_token = localStorage.getItem('access_token');
const refresh_token = localStorage.getItem('refresh_token');
if (access_token && refresh_token) {
  authStore.setTokens(access_token, refresh_token);
} else {
  authStore.setUserInfo(null, null, null, null, null);
  authStore.setTokens(null, null);
  router.push('/loginpage');
}

</script>
