<template>
  <v-app>
    <v-card>
      <v-layout>
        <v-navigation-drawer permanent expand-on-hover rail>
          <v-list>
            <v-list-item @click="router.push('/profile')" :prepend-avatar="user.avatar || placeholderAvatar"
              :subtitle="user.email" :title="user.name + ' ' + user.surname"></v-list-item>
          </v-list>

          <v-divider></v-divider>

          <v-list density="compact" nav>
            <v-list-item prepend-icon="mdi-folder-multiple" title="Projects" value="projects"
              @click="goToProjectList()"></v-list-item>
            <v-list-item prepend-icon="mdi-chart-timeline" title="Timeline" value="timeline"
              @click="router.push('/timeline')"></v-list-item>
            <v-list-item prepend-icon="mdi-format-list-bulleted" title="Backlog" value="backlog"
              @click="router.push('/backlog')"></v-list-item>
            <v-list-item prepend-icon="mdi-view-dashboard" title="Board" value="board"
              @click="router.push('/board')"></v-list-item>
            <v-list-item prepend-icon="mdi-finance" title="Analitycs" value="analitycs"
              @click="router.push('/analitycs')"></v-list-item>
            <v-list-item v-if="false" prepend-icon="mdi-notebook-edit" title="Pages" value="pages" 
              @click="router.push('/pages')"></v-list-item>
            <v-list-item v-if="false" prepend-icon="mdi-bell" title="Notifications" value="notifications"
              @click="router.push('/notifications')"></v-list-item>
            <v-list-item prepend-icon="mdi-cog" title="Settings" value="settings"
              @click="router.push('/settings')"></v-list-item>
          </v-list>
        </v-navigation-drawer>

        <v-main style="min-height: 100vh">
          <router-view />
        </v-main>
      </v-layout>
    </v-card>
  </v-app>
</template>
<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { showReLoginDialog } from '@/utils/authFetch';
import { useAuthStore } from '@/stores/auth';
import { useProjectStore } from '@/stores/project';

const auth = useAuthStore();
const projectStore = useProjectStore();

const user = ref({
  name: '',
  surname: '',
  email: '',
  password: '',
  avatar: '',
});

const placeholderAvatar = ref("src/assets/avatar.jpg");

const goToProjectList = () => {
  projectStore.setProjectInfo(null, null, null, null, null, null);
  localStorage.removeItem("currentProject");
  localStorage.removeItem("currentProjectRole");
  router.push('/projectslist')
};

onMounted(() => {
  const { name, surname, email, password, img_url } = auth.getUserInfo();
  if (!name || !surname || !email) {
    const userLocal = JSON.parse(localStorage.getItem("user"))
    if (userLocal) {
      showReLoginDialog();
    }
    user.value.name = userLocal.name;
    user.value.surname = userLocal.surname;
    user.value.email = userLocal.email;
    user.value.password = userLocal.password;
    user.value.avatar = userLocal.imgUrl;

    auth.setUserInfo(userLocal.email, userLocal.password, userLocal.name, userLocal.surname, userLocal.imgUrl);
  }
  else {
    user.value.name = name;
    user.value.surname = surname;
    user.value.email = email;
    user.value.password = password;
    user.value.avatar = img_url;
  } 
});

const router = useRouter();
</script>