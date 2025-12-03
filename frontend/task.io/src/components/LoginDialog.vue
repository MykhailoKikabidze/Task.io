<template>
  <v-dialog v-model="model" width="400" persistent>
    <v-card class="pa-4">
      <v-card-title class="text-h6 justify-center">
        Session Expired
      </v-card-title>
      <v-card-text class="text-body-1 text-center">
        Your session has expired. Please log in again to continue working.
      </v-card-text>
      <v-card-actions class="justify-center">
        <v-btn color="primary" @click="onLogin">Go to Login</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})
const emit = defineEmits(['update:modelValue'])

const router = useRouter()

const model = computed({
  get: () => props.modelValue,
  set: v => emit('update:modelValue', v)
})

function onLogin() {
  model.value = false
  router.push('/loginpage')
}
</script>

<style scoped>
.v-card {
  background-color: #2a2a2a;
  color: #fff;
}
</style>
