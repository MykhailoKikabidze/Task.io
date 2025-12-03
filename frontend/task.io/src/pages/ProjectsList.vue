<template>
  <v-app>
    <v-app-bar dense dark>
      <v-avatar class="ml-4" @click="router.push('/profile')">
        <v-img :src="user.avatar || placeholderAvatar" />
      </v-avatar>

      <div class="ml-4">
        <div class="user-name">{{ user.name }}</div>
        <div class="user-email">{{ user.email }}</div>
      </div>

      <v-spacer />

      <v-btn icon @click="logout" @mouseenter="isHovered = true" @mouseleave="isHovered = false">
        <v-icon>{{ isHovered ? 'mdi-logout-variant' : 'mdi-logout' }}</v-icon>
      </v-btn>
    </v-app-bar>

    <v-container class="list-of-projects">
      <v-row class="align-center mb-2">
        <h2 class="title">Your Projects</h2>
        <v-spacer />
        <v-tooltip text="New project" location="bottom">
          <template #activator="{ props }">
            <v-btn icon v-bind="props" @click="showDialog = true">
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </template>
        </v-tooltip>
      </v-row>

      <v-divider class="border-opacity-75 mb-3" />

      <v-row>
        <v-col v-for="project in projects" :key="project.id" cols="12" sm="6" md="4">
          <v-card class="project-card" :style="{ borderLeft: `8px solid ${project.color}` }">
            <v-card-title class="d-flex align-center">
              <v-avatar class="project-avatar mr-2">
                <v-img v-if="project.icon" :src="project.icon" alt="icon" />
                <span v-else class="text-white">{{ project.initials }}</span>
              </v-avatar>
              {{ project.name }}
            </v-card-title>

            <v-card-subtitle>{{ project.type }}</v-card-subtitle>

            <v-card-text>
              <p class="mb-2">Quick links</p>
              <v-list density="compact">
                <v-list-item @click="goToBacklog(project.id)" clickable>
                  <v-icon class="mr-2">mdi-format-list-bulleted</v-icon>
                  Backlog
                </v-list-item>

                <v-list-item @click="goToSettings(project.id)" clickable>
                  <v-icon class="mr-2">mdi-cog</v-icon>
                  Settings
                </v-list-item>

                <v-list-item v-if="false" @click="goToNotifications(project.id)" clickable>
                  <v-icon class="mr-2">mdi-bell</v-icon>
                  Notifications
                </v-list-item>
              </v-list>
            </v-card-text>

            <v-card-actions>
              <v-btn text color="primary" @click="goToProject(project.id)">View project</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <v-dialog v-model="showDialog" width="600" persistent>
      <v-card>
        <v-card-title>Create new project</v-card-title>
        <v-card-text>
          <v-text-field v-model="newProject.name" label="Project name *" prepend-inner-icon="mdi-format-title" outlined
            dense required />

          <v-select v-model="newProject.type" :items="typeOptions" item-title="title" item-value="value"
            label="Project type *" prepend-inner-icon="mdi-format-list-bulleted" outlined dense />

          <v-textarea v-model="newProject.description" label="Description *" rows="3" auto-grow
            prepend-inner-icon="mdi-text-box-outline" outlined dense />

          <v-autocomplete v-model="selectedUsers" v-model:search="userSearch" :items="userOptions" item-title="label"
            return-object multiple chips clearable cache-items :loading="loadingUsers" :filter="() => true"
            label="Add users *" prepend-inner-icon="mdi-account-multiple-plus" outlined dense
            @update:search="onUserSearch" />

          <v-divider class="my-2" />
          <div v-if="newProject.users.length" class="mb-2">
            <div class="text-subtitle-2 mb-1">Assigned Users:</div>
            <v-card v-for="(u, idx) in newProject.users" :key="u.id" class="pa-2 mb-2 d-flex align-center"
              color="grey-darken-3">
              <v-avatar size="28" class="mr-2">
                <v-img v-if="u.img_url" :src="u.img_url" />
                <span v-else class="white--text" style="font-size:14px;">
                  {{ u.name.slice(0, 1) }}
                </span>
              </v-avatar>
              <div class="mr-4">{{ u.name }}</div>
              <v-select v-model="u.role" :items="roleOptionsUI" item-title="label" item-value="value" label="Role" dense
                hide-details class="ml-auto" style="max-width: 160px;" />
            </v-card>
          </div>

          <v-select v-model="newProject.color" :items="colorOptions" item-title="title" item-value="value"
            label="Project color *" prepend-inner-icon="mdi-palette" outlined dense @update:modelValue="onColorChange"
            class="mt-2">
            <template #item="{ props, item }">
              <v-list-item v-bind="props">
                <v-icon class="mr-2" :style="{ color: item.value }">mdi-circle</v-icon>
                {{ item.title }}
              </v-list-item>
            </template>
            <template #selection="{ item }">
              <v-chip v-if="item.value !== 'custom'" class="ma-1"
                :style="{ backgroundColor: item.value, color: '#fff' }">
                {{ item.title }}
              </v-chip>
              <v-chip v-else class="ma-1" color="grey darken-1" text-color="white">
                Custom…
              </v-chip>
            </template>
          </v-select>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn text @click="resetDialog">Cancel</v-btn>
          <v-btn color="primary" @click="createProject" :disabled="!isValid">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="showColorPicker" width="340">
      <v-card>
        <v-card-text class="pa-4">
          <v-color-picker v-model="customColor" hide-mode-switch hide-inputs swatches-max-height="160" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="showColorPicker = false">Cancel</v-btn>
          <v-btn color="primary" @click="applyCustomColor">OK</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-app>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useProjectStore } from '@/stores/project';
import { authFetch } from '@/utils/authFetch';

const router = useRouter();
const authStore = useAuthStore();
const projectStore = useProjectStore();
const isHovered = ref(false);
const placeholderAvatar = ref("/src/assets/avatar.jpg");

const showDialog = ref(false);
const showColorPicker = ref(false);
const customColor = ref('#1E88E5');


const colorOptions = [
  { title: 'Red', value: '#E53935' },
  { title: 'Pink', value: '#D81B60' },
  { title: 'Purple', value: '#8E24AA' },
  { title: 'Deep purple', value: '#5E35B1' },
  { title: 'Indigo', value: '#3949AB' },
  { title: 'Blue', value: '#1E88E5' },
  { title: 'Cyan', value: '#00ACC1' },
  { title: 'Teal', value: '#00897B' },
  { title: 'Green', value: '#43A047' },
  { title: 'Lime', value: '#C0CA33' },
  { title: 'Amber', value: '#FFB300' },
  { title: 'Orange', value: '#FB8C00' },
  { title: 'Deep orange', value: '#F4511E' },
  { title: 'Brown', value: '#6D4C41' },
  { title: 'Blue Grey', value: '#546E7A' },
  { title: 'Custom…', value: 'custom' }
];

const projects = ref([]);

async function goToProject(id) {
  try {
    await loadProjectIntoStore(id);
    router.push('/board');
  } catch (e) {
    console.error(e);
  }
}

async function goToBacklog(id) {
  try {
    await loadProjectIntoStore(id);
    router.push('/backlog');
  } catch (e) {
    console.error(e);
  }
}

async function goToNotifications(id) {
  try {
    await loadProjectIntoStore(id);
    router.push('/notifications');
  } catch (e) {
    console.error(e);
  }
}

async function goToSettings(id) {
  try {
    await loadProjectIntoStore(id);
    router.push('/settings');
  } catch (e) {
    console.error(e);
  }
}


const newProject = ref({
  name: '',
  type: '',
  description: '',
  users: [],
  color: colorOptions[0].value
});

const auth = useAuthStore();

const user = ref({
  name: '',
  email: '',
  avatar: '',
  initials: ''
});

const isValid = computed(() => {
  return newProject.value.name.trim() &&
    newProject.value.description.trim() &&
    newProject.value.type &&
    newProject.value.users &&
    newProject.value.color
});

const typeOptions = [
  { title: 'Pet-project', value: 'pet-project' },
  { title: 'Software', value: 'software' },
  { title: 'Bugtracking', value: 'bugtracking' },
  { title: 'DevOps', value: 'devops' },
  { title: 'Project management', value: 'project managment' },
  { title: 'Marketing', value: 'marketing' },
  { title: 'Finance', value: 'finance' },
  { title: 'Science', value: 'science' },
  { title: 'Event organization', value: 'event organization' },
];

const userSearch = ref('');
const selectedUsers = ref([]);
const userOptions = ref([]);
const loadingUsers = ref(false);


async function logout() {
  try {
    await authFetch('/api/v1/auth/logout', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${auth.access_token}`,
      },
      credentials: 'include'
    });
  } catch (e) {
    console.warn('Logout request failed, but proceeding anyway');
  }

  auth.setTokens(null, null);
  auth.setUserInfo(null, null, null, null);
  auth.setUserId(null);

  localStorage.removeItem("user");
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");

  router.push('/loginpage');
}

onMounted(async () => {
  const { name, surname, email, img_url } = auth.getUserInfo();
  user.value.name = `${name} ${surname}`;
  user.value.email = email;
  user.value.avatar = img_url;
  user.value.initials = name?.[0]?.toUpperCase() || '';

  await fetchProjects();
});

const mapApiProject = (p) => ({
  id: p.id,
  name: p.name,
  type: p.type,
  color: p.color || '#1E88E5',
  icon: p.img_url || '',
  initials: (p.name?.[0] || '').toUpperCase(),
});

const fetchProjects = async () => {
  const token = auth.getAccessToken();
  const res = await authFetch('/api/v1/pm/me/projects');
  if (!res.ok) throw new Error('Failed to load projects');
  const data = await res.json();
  projects.value = (data.projects || []).map(mapApiProject);
};

async function onUserSearch(q) {
  if (!q || q.length < 2) { userOptions.value = []; return; }
  loadingUsers.value = true;
  try {
    const res = await authFetch(`/api/v1/auth/search?substr=${encodeURIComponent(q)}`);
    if (res.ok) {
      const meId = localStorage.getItem('user_id');
      const arr = await res.json();
      userOptions.value = arr.filter(u => u.user_id !== meId)
        .map(u => ({
          id: u.user_id,
          name: u.name,
          surname: u.surname,
          email: u.email,
          label: `${u.name} ${u.surname} — ${u.email}`
        }));
    } else {
      userOptions.value = [];
    }
  } finally {
    loadingUsers.value = false;
  }
}

async function fetchUserById(userId) {
  if (!userId) return null;

  try {
    const res = await authFetch(`/api/v1/auth/user/${encodeURIComponent(userId)}`);
    if (!res.ok) return null;

    const data = await res.json();
    const user = {
      id: data.user_id || userId,
      name: data.name || '',
      surname: data.surname || '',
      email: data.email || '',
      img_url: data.img_url || '',
    };
    return user;
  } catch (e) {
    console.error('fetchUserById error:', e);
    return null;
  }
}

watch(selectedUsers, async (arr) => {
  const prev = new Map(newProject.value.users.map(u => [u.id, u]));

  const meId = authStore.getUserId();
  const meInfo = authStore.getUserInfo();

  const list = [];
  list.push({
    id: meId,
    name: `${meInfo.name} ${meInfo.surname}`,
    role: 'owner',
    img_url: meInfo.img_url || ''
  });

  const rest = await Promise.all(
    arr
      .filter(u => u.id !== meId)
      .map(async (u) => {
        const full = await fetchUserById(u.id);
        return {
          id: u.id,
          name: `${u.name} ${u.surname}`,
          role: prev.get(u.id)?.role || 'observer',
          img_url: full?.img_url || ''
        };
      })
  );

  newProject.value.users = [...list, ...rest];

  if (newProject.value.users.length > prev.size) {
    userSearch.value = '';
    userOptions.value = [];
  }
});



const roleOptions = ['observer', 'assignee', 'manager', 'owner'];
const roleOptionsUI = roleOptions.map(r => ({ label: r[0].toUpperCase() + r.slice(1), value: r }));

const createProject = async () => {
  if (!newProject.value.name.trim()) return;

  const payload = {
    name: newProject.value.name,
    description: newProject.value.description || '',
    color: newProject.value.color,
    img_url: '',
    type: newProject.value.type,
    users: newProject.value.users.map(u => ({ id: u.id, role: u.role }))
  };

  const res = await authFetch('/api/v1/pm/project', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    console.error('Create project failed');
    return;
  }

  const created = await res.json();
  projects.value.push(mapApiProject(created));
  resetDialog();
};

watch(showDialog, (open) => {
  if (!open) return;
  const { name, surname, img_url } = authStore.getUserInfo();
  const meId = authStore.getUserId();

  newProject.value = {
    name: '',
    type: '',
    description: '',
    color: colorOptions[0].value,
    users: [{ id: meId, name: `${name} ${surname}`, role: 'owner', img_url: img_url }]
  };
  selectedUsers.value = [];
});

const onColorChange = val => {
  if (val === 'custom') {
    showColorPicker.value = true;
  }
};

const applyCustomColor = () => {
  newProject.value.color = customColor.value;
  showColorPicker.value = false;
};

const resetDialog = () => {
  newProject.value = {
    name: '',
    type: '',
    description: '',
    users: [],
    color: colorOptions[0].value
  };
  selectedUsers.value = [];
  showDialog.value = false;
};

async function loadProjectIntoStore(projectId) {
  const res = await authFetch(`/api/v1/pm/project?project_id=${encodeURIComponent(projectId)}`);
  if (!res.ok) throw new Error('Failed to load project');
  const p = await res.json();

  projectStore.setProjectInfo(p.id, p.name, p.description, p.color, p.img_url, p.type);
  localStorage.setItem("currentProject", JSON.stringify({
    id: p.id,
    name: p.name,
    description: p.description,
    color: p.color,
    img_url: p.img_url,
    type: p.type
  }))

  const myId = localStorage.getItem("user_id");

  const result = await authFetch(`/api/v1/pm/project/users?project_id=${encodeURIComponent(projectId)}`);
  if (!result.ok) {
    console.error('Failed to load project users');
    projectStore.setRole('observer');
    return;
  }

  const { users = [] } = await result.json();

  const me = users.find(u => String(u.id) === String(myId));
  projectStore.setRole(me?.role ?? 'observer');

  console.log('My role in project:', me?.role);

  switch (me.role) {
    case 'owner':
      localStorage.setItem("currentProjectRole", 0);
      break;
    case 'manager':
      localStorage.setItem("currentProjectRole", 1);
      break;
    case 'assignee':
      localStorage.setItem("currentProjectRole", 2);
      break;
    case 'observer':
      localStorage.setItem("currentProjectRole", 3);
      break;
    default:
      localStorage.setItem("currentProjectRole", 3);
  }

}
</script>

<style scoped>
.list-of-projects {
  margin-top: 5%;
}

.title {
  font-family: Arial;
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 6px;
}

.project-card {
  border-radius: 8px;
  overflow: hidden;
  transition: box-shadow 0.3s;
}

.project-avatar {
  background-color: #555;
  color: white;
  font-weight: bold;
  font-size: 20px;
}

.project-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.25);
}

.user-name {
  font-weight: bold;
  font-size: 14px;
}

.user-email {
  font-size: 12px;
  opacity: 0.8;
}
</style>
