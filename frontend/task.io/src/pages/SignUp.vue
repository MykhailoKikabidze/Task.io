<template>
  <div class="fullscreen-container">
    <v-card class="mx-auto pa-12 pb-8" elevation="8" max-width="448" rounded="lg">
      <div class="text-subtitle-1 text-medium-emphasis">Account</div>

      <v-text-field v-model="firstName" :error-messages="firstNameError" @input="validateFirstName" density="compact"
        placeholder="First name *" prepend-inner-icon="mdi-account" variant="outlined"></v-text-field>

      <v-text-field v-model="lastName" :error-messages="lastNameError" @input="validateLastName" density="compact"
        placeholder="Last name *" prepend-inner-icon="mdi-account" variant="outlined"></v-text-field>

      <v-text-field v-model="email" :error-messages="emailError" @input="validateEmail" density="compact"
        placeholder="Email address *" prepend-inner-icon="mdi-email-outline" variant="outlined"></v-text-field>

      <div class="text-subtitle-1 text-medium-emphasis d-flex align-center justify-space-between">
        Password
      </div>

      <v-text-field v-model="password" :error-messages="passwordError" @input="validatePassword"
        :append-inner-icon="visible ? 'mdi-eye-off' : 'mdi-eye'" :type="visible ? 'text' : 'password'" density="compact"
        placeholder="Enter your password *" prepend-inner-icon="mdi-lock-outline" variant="outlined"
        @click:append-inner="visible = !visible"></v-text-field>

      <v-text-field v-model="repeatPassword" :error-messages="repeatPasswordError" @input="validateRepeatPassword"
        type="password" density="compact" placeholder="Repeat your password *" prepend-inner-icon="mdi-lock-outline"
        variant="outlined" @click:append-inner="visible = !visible"></v-text-field>

      <v-card class="mb-12" color="surface-variant" variant="tonal">
      </v-card>

      <v-btn block @click="handleSignUp" :disabled="!isFormValid" class="mb-8" color="blue" size="large"
        variant="tonal">
        Create account
      </v-btn>

      <v-card-text class="text-center">
        <router-link to="/loginpage" class="text-blue text-decoration-none">
          Login now <v-icon icon="mdi-chevron-right"></v-icon>
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

const router = useRouter();
const visible = ref(false);

const firstName = ref('');
const lastName = ref('');
const email = ref('');
const password = ref('');
const repeatPassword = ref('');

const firstNameError = ref('');
const lastNameError = ref('');
const emailError = ref('');
const passwordError = ref('');
const repeatPasswordError = ref('');

const snackbarMessage = ref('');
const snackbarVisible = ref(false);

const validateFirstName = () => {
  if (!firstName.value) {
    firstNameError.value = '';
    return;
  }

  const nameRegex = /^[A-Z][a-z]+$/;
  firstNameError.value = nameRegex.test(firstName.value) ? '' : 'First name must start with a capital letter';
};

const validateLastName = () => {
  if (!lastName.value) {
    lastNameError.value = '';
    return;
  }

  const nameRegex = /^[A-Z][a-z]+$/;
  lastNameError.value = nameRegex.test(lastName.value) ? '' : 'Last name must start with a capital letter';
};

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

const validateRepeatPassword = () => {
  if (!repeatPassword.value) {
    repeatPasswordError.value = '';
    return;
  }

  repeatPasswordError.value = repeatPassword.value === password.value ? '' : 'Passwords do not match';
};

const isFormValid = computed(() =>
  !firstNameError.value &&
  !lastNameError.value &&
  !emailError.value &&
  !passwordError.value &&
  !repeatPasswordError.value &&
  firstName.value &&
  lastName.value &&
  email.value &&
  password.value &&
  repeatPassword.value
);

const handleSignUp = async () => {
  console.log('Signing up with:', firstName.value, lastName.value, email.value, password.value);

  try {
    const singupResponse = await fetch('http://localhost:8000/api/v1/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: firstName.value,
        surname: lastName.value,
        email: email.value,
        password: password.value,
        img_url: ""
      })
    });

    const response = await singupResponse.json();
    console.log('Sign-up response:', response);

    if (singupResponse.ok) {
      console.log('Sign-up successful');
      router.push('/loginpage');
      return;
    }

    const match = response.detail.match(/User with this email already exists/);

    if (match) {
      snackbarMessage.value = 'User with this email already exists';
    } else {
      snackbarMessage.value = response.detail || 'Sing up failed';
    }

    snackbarVisible.value = true;

    setTimeout(() => {
      snackbarVisible.value = false;
      snackbarMessage.value = '';
    }, 3000);

    console.error('Sign-up failed:', response);
  } catch (error) {
    console.error('Sign-up error:', error);
  }
}
</script>

<style scoped>
.fullscreen-container {
  margin-top: 10%;
}
</style>