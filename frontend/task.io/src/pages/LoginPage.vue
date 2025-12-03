<template>
  <div class="fullscreen-container">
    <v-card class="mx-auto pa-12 pb-8" elevation="8" max-width="448" rounded="lg">
      <div class="text-subtitle-1 text-medium-emphasis">Account</div>

      <v-text-field v-model="email" :error-messages="emailError" @input="validateEmail" density="compact"
        placeholder="Email address" prepend-inner-icon="mdi-email-outline" variant="outlined"></v-text-field>

      <div class="text-subtitle-1 text-medium-emphasis d-flex align-center justify-space-between">
        Password
      </div>

      <v-text-field v-model="password" :error-messages="passwordError" @input="validatePassword"
        :append-inner-icon="visible ? 'mdi-eye-off' : 'mdi-eye'" :type="visible ? 'text' : 'password'" density="compact"
        placeholder="Enter your password" prepend-inner-icon="mdi-lock-outline" variant="outlined"
        @click:append-inner="visible = !visible"></v-text-field>

      <v-card class="mb-12" color="surface-variant" variant="tonal">
      </v-card>

      <v-btn block @click="handleLogin" :disabled="!isFormValid" class="mb-8" color="blue" size="large" variant="tonal">
        Log In
      </v-btn>

      <v-card-text class="text-center">
        <router-link to="/signup" class="text-blue text-decoration-none">
          Sign up now <v-icon icon="mdi-chevron-right"></v-icon>
        </router-link>
      </v-card-text>

      <v-snackbar v-model="snackbarVisible" color="red" timeout="3000">
        <div class="text-center">
          {{ snackbarMessage }}
        </div>
      </v-snackbar>

    </v-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router';
import { authFetch } from '@/utils/authFetch';
import { useAuthStore } from '@/stores/auth';


const router = useRouter();
const visible = ref(false)

const email = ref('');
const password = ref('');

const emailError = ref('');
const passwordError = ref('');

const snackbarMessage = ref('');
const snackbarVisible = ref(false);

const authStore = useAuthStore();

const validateEmail = () => {
  if (!email.value) {
    emailError.value = '';
    return;
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  emailError.value = emailRegex.test(email.value) ? '' : 'Invalid email address';
};

const validatePassword = () => {
  if (!password.value) {
    passwordError.value = '';
    return;
  }

  const passwordRegex = /^.*(?=.{8,})(?=.*[a-zA-Z])(?=.*\d)(?=.*[!#$%&? "]).*$/;
  passwordError.value = passwordRegex.test(password.value)
    ? ''
    : 'Password must be at least 8 characters long, include a number, a letter, and a special character';
};

const isFormValid = computed(() => !emailError.value && !passwordError.value && email.value && password.value);

const handleLogin = async () => {

  try {
    const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: email.value,
        password: password.value
      }),
      credentials: 'include'
    });

    if (!loginResponse.ok) {
      const errorData = await loginResponse.json();

      const match = errorData.detail.match(/Invalid credentials/);

      if (match) {
        snackbarMessage.value = 'Invalid email or password';
      } else {
        snackbarMessage.value = errorData.detail || 'Login failed';
      }

      snackbarVisible.value = true;

      setTimeout(() => {
        snackbarVisible.value = false;
        snackbarMessage.value = '';
      }, 3000);
      return;
    }

    const data = await loginResponse.json();

    authStore.setTokens(data.access_token, data.refresh_token);

    const meRes = await authFetch('/api/v1/auth/me', {
      headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${authStore.getAccessToken()}`
      },
      credentials: 'include'
    });

    if (!meRes.ok) {
      authStore.setTokens(null, null);
      snackbarMessage.value = 'Failed to load user profile';
      snackbarVisible.value = true;

      setTimeout(() => {
        snackbarVisible.value = false;
        snackbarMessage.value = '';
      }, 3000);
      return;
    }

    const meData = await meRes.json();

    authStore.setUserInfo(
      meData.email,
      password.value,
      meData.name,
      meData.surname,
      meData.img_url
    );

    authStore.setUserId(meData.user_id);

    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);

    localStorage.setItem("user", JSON.stringify({
      name: meData.name,
      surname: meData.surname,
      email: meData.email,
      imgUrl: meData.img_url,
      password: password.value,
    }));

    localStorage.setItem("user_id", meData.user_id);

    router.push('/projectslist');
  } catch (error) {
    console.error('Login error:', error);
    snackbarMessage.value = 'Network error or server unavailable';
    snackbarVisible.value = true;

    setTimeout(() => {
      snackbarVisible.value = false;
      snackbarMessage.value = '';
    }, 3000);
  }
};
</script>

<style scoped>
.fullscreen-container {
  margin-top: 10%;
}
</style>