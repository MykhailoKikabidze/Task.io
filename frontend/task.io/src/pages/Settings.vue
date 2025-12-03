<route lang="yaml">
  meta:
    layout: navigation
</route>

<template>
  <v-container class="settings-container">
    <v-card class="pa-6" elevation="8" rounded="lg" width="600">
      <h2 class="text-h5 font-weight-bold mb-4">Project Settings</h2>

      <div class="d-flex justify-center mb-6">
        <v-avatar size="100" class="project-avatar">
          <v-img v-if="project.avatar" :src="project.avatar" alt="icon" />
          <span v-else class="text-white">{{ project.name[0] }}</span>
        </v-avatar>

        <v-btn icon class="avatar-btn" @click="triggerFileInput" :disabled="myRole > 1">
          <v-icon>mdi-camera</v-icon>
        </v-btn>
        <input ref="fileInput" type="file" accept="image/png, image/jpeg" class="d-none" @change="onAvatarSelected" />
      </div>

      <v-text-field v-model="project.name" label="Project Name *" prepend-inner-icon="mdi-format-title"
        variant="outlined" density="compact" class="mb-3" required :disabled="myRole > 1" />

      <v-select v-model="project.type" :items="typeOptions" item-title="title" item-value="value" label="Project Type *"
        prepend-inner-icon="mdi-briefcase-outline" variant="outlined" density="compact" class="mb-3"
        :disabled="myRole > 1" />


      <v-textarea v-model="project.description" label="Project Description *" rows="4" auto-grow
        prepend-inner-icon="mdi-text-box-outline" variant="outlined" density="compact" class="mb-3"
        :disabled="myRole > 1" />

      <v-select v-model="project.color" :items="colorOptions" item-title="title" item-value="value"
        label="Project Color *" prepend-inner-icon="mdi-palette" variant="outlined" density="compact" class="mb-4"
        @update:modelValue="onColorChange" :disabled="myRole > 1">
        <template #item="{ props, item }">
          <v-list-item v-bind="props">
            <v-icon class="mr-2" :style="{ color: item.value }">mdi-circle</v-icon>
            {{ item.title }}
          </v-list-item>
        </template>
        <template #selection="{ item }">
          <v-chip v-if="item.value !== 'custom'" class="ma-1" :style="{ backgroundColor: item.value, color: '#fff' }">
            {{ item.title }}
          </v-chip>
          <v-chip v-else class="ma-1" color="grey darken-1" text-color="white">
            Custom…
          </v-chip>
        </template>
      </v-select>

      <v-autocomplete v-model="selectedToAdd" :disabled="myRole > 1" v-model:search="userSearch" :items="userOptions"
        item-title="label" return-object multiple chips clearable cache-items :loading="loadingUsers"
        :filter="() => true" label="Add collaborators *" prepend-inner-icon="mdi-account-multiple-plus"
        variant="outlined" density="compact" @update:search="onUserSearch">
        <template #selection="{ item }">
          <v-chip closable @click:close="removeUser(item.raw.id)">
            {{ item.raw.label }}
          </v-chip>
        </template>
      </v-autocomplete>

      <div v-if="projectUsers.length" class="mb-4">
        <div class="text-subtitle-2 mb-2">Collaborators & Roles:</div>

        <div v-for="u in projectUsers" :key="u.id" class="pa-2 mb-2 d-flex align-center collaborator-row">
          <v-avatar size="28" class="mr-3">
            <v-img v-if="u.img_url" :src="u.img_url" />
            <span v-else class="white--text">{{ u.name.charAt(0) }}</span>
          </v-avatar>

          <div class="mr-4">{{ u.name }}</div>

          <v-select v-model="u.role" :disabled="!canEditRole(u)" :items="roleItemsForUser(u)" item-title="label" item-value="value"
            label="Role" dense hide-details class="ml-auto" style="max-width: 190px;" />

          <v-icon :disabled="myRole > 1" small color="red lighten-1" class="ml-2"
            @click="removeUser(u.id)">mdi-close-circle</v-icon>
        </div>
      </div>


      <v-row dense>
        <v-col cols="6" v-if="myRole <= 1">
          <v-btn color="blue" :disabled="!isValid" block @click="saveChanges">
            Save Changes
          </v-btn>
        </v-col>
        <v-col cols="6" v-if="myRole == 0">
          <v-btn color="red" block @click="showDelete = true">Delete Project</v-btn>
        </v-col>
      </v-row>
    </v-card>

    <v-dialog v-model="showDelete" width="400">
      <v-card>
        <v-card-title class="text-h6">Delete project?</v-card-title>
        <v-card-text>
          This cannot be undone. Are you sure you want to delete
          <strong>{{ project.name }}</strong>?
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="showDelete = false">Cancel</v-btn>
          <v-btn color="red" @click="deleteProject">Delete</v-btn>
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

    <v-snackbar v-model="showSnackbar" :timeout="2000" location="bottom center" :color="snackbarColor" elevation="4">
      <div class="text-center w-100">{{ snackbarMessage }}</div>

      <template #action="{ attrs }">
        <v-btn icon v-bind="attrs" @click="showSnackbar = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </template>
    </v-snackbar>

  </v-container>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProjectStore } from '@/stores/project'
import { authFetch } from '@/utils/authFetch'
const router = useRouter();
const authStore = useAuthStore()
const projectStore = useProjectStore()
let myRole = ref(3)

const project = ref({
  id: null,
  name: '',
  description: '',
  color: '#1E88E5',
  type: '',
  avatar: ''
})

const projectUsers = ref([])

onMounted(async () => {
  const p = JSON.parse(localStorage.getItem("currentProject"))

  myRole = localStorage.getItem("currentProjectRole") || 3

  console.log('Current Role:', myRole)

  if (!p.id) {
    const projectLocal = JSON.parse(localStorage.getItem("currentProject"))

    if (projectLocal) {
      projectStore.setProjectInfo(projectLocal.id, projectLocal.name, projectLocal.description, projectLocal.color, projectLocal.img_url, projectLocal.type);
      Object.assign(project.value, {
        id: projectLocal.id,
        name: projectLocal.name,
        description: projectLocal.description || '',
        color: projectLocal.color || '#1E88E5',
        type: projectLocal.type || '',
        avatar: projectLocal.img_url || ''
      })
      await loadProjectUsers(projectLocal.id)
      return
    }
    router.push('/projectslist')
    return
  }

  Object.assign(project.value, {
    id: p.id,
    name: p.name,
    description: p.description || '',
    color: p.color || '#1E88E5',
    type: p.type || '',
    avatar: p.img_url || ''
  })

  await loadProjectUsers(p.id)
})

async function loadProjectUsers(projectId) {
  const res = await authFetch(`/api/v1/pm/project/users?project_id=${encodeURIComponent(projectId)}`)
  if (!res.ok) throw new Error('Failed to load project users')
  const data = await res.json()

  projectUsers.value = (data.users || []).map(u => ({
    id: u.id,
    name: `${u.name} ${u.surname}`,
    email: u.email,
    img_url: u.img_url,
    role: u.role || 'observer',
    originalRole: u.role || 'observer'
  }))

  await populateMissingAvatars(projectUsers.value)
}

const _userByIdCache = new Map()
async function fetchUserById(userId) {
  if (!userId) return null
  if (_userByIdCache.has(userId)) return _userByIdCache.get(userId)

  try {
    const res = await authFetch(`/api/v1/auth/user/${encodeURIComponent(userId)}`)
    if (!res.ok) return null
    const data = await res.json()

    const user = {
      id: data.user_id || userId,
      name: data.name || '',
      surname: data.surname || '',
      email: data.email || '',
      img_url: data.img_url || ''
    }
    _userByIdCache.set(userId, user)
    return user
  } catch (e) {
    console.error('fetchUserById error:', e)
    return null
  }
}

async function populateMissingAvatars(list) {
  await Promise.all(
    list
      .filter(u => !u.img_url)
      .map(async u => {
        const prof = await fetchUserById(u.id)
        if (prof) {
          if (!u.img_url && prof.img_url) u.img_url = prof.img_url
          if (!u.name || !u.name.trim()) {
            u.name = `${prof.name || ''} ${prof.surname || ''}`.trim()
          }
        }
      })
  )
}


const canEditRole = (u) => {
  console.log('Can edit role check:', { myRole: myRole, user: u.originalRole })

  if (myRole == 0) return true;
  if (myRole == 1 && (u.originalRole === 'owner' || u.originalRole === 'manager')) return false;
  if (myRole == 1) return true;

  return false;
}


const roleItemsForUser = (u) => {
  if (myRole == 1) return roleOptionsUI.filter(o => o.value !== 'owner')
  return roleOptionsUI
}


const userSearch = ref('');
const userOptions = ref([])
const loadingUsers = ref(false)
const selectedToAdd = ref([])

async function onUserSearch(q) {
  if (!q || q.length < 2) { userOptions.value = []; return }
  loadingUsers.value = true
  try {
    const res = await authFetch(`/api/v1/auth/search?substr=${encodeURIComponent(q)}`)
    if (!res.ok) { userOptions.value = []; return }
    const meId = authStore.getUserId()
    const already = new Set(projectUsers.value.map(u => u.id))

    const arr = await res.json()
    userOptions.value = arr
      .filter(u => u.user_id !== meId && !already.has(u.user_id))
      .map(u => ({
        id: u.user_id,
        name: u.name,
        surname: u.surname,
        email: u.email,
        label: `${u.name} ${u.surname} — ${u.email}`
      }))
  } finally {
    loadingUsers.value = false
  }
}

watch(selectedToAdd, async (arr) => {
  const newlyAdded = []

  for (const u of arr) {
    if (projectUsers.value.find(x => x.id === u.id)) continue
    const row = {
      id: u.id,
      name: `${u.name} ${u.surname}`,
      email: u.email,
      img_url: '',
      role: 'observer',
      originalRole: 'observer',
    }
    projectUsers.value.push(row)
    newlyAdded.push(row)
  }

  if (newlyAdded.length) {
    await populateMissingAvatars(newlyAdded)
    userSearch.value = ''
    userOptions.value = []
  }
})


let roleOptions = ['observer', 'assignee', 'manager', 'owner']
const roleOptionsUI = roleOptions.map(r => ({ label: r[0].toUpperCase() + r.slice(1), value: r }))

function removeUser(userId) {
  const meId = authStore.getUserId()
  if (userId === meId) return
  projectUsers.value = projectUsers.value.filter(u => u.id !== userId)
  selectedToAdd.value = selectedToAdd.value.filter(u => u.id !== userId)
}

const placeholderAvatar = '/src/assets/default.png'
const fileInput = ref(null)
const avatarFile = ref(null)
const isDirtyAvatar = ref(false)

const triggerFileInput = () => fileInput.value?.click()

function onAvatarSelected(e) {
  const file = e.target.files?.[0]
  if (!file) return
  if (!/^image\/(png|jpeg)$/.test(file.type)) return
  const reader = new FileReader()
  reader.onload = evt => {
    project.value.avatar = evt.target.result
    avatarFile.value = file
    isDirtyAvatar.value = true
  }
  reader.readAsDataURL(file)
}

async function saveChanges() {
  try {
    const r1 = await authFetch('/api/v1/pm/project', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: project.value.id,
        name: project.value.name,
        description: project.value.description || '',
        color: project.value.color,
        type: project.value.type,
      }),
    });
    if (!r1.ok) throw new Error('Failed to update project info');

    if (isDirtyAvatar.value && avatarFile.value) {
      const form = new FormData();
      form.append('file', avatarFile.value);
      const r2 = await authFetch(`/api/v1/pm/project/img/${project.value.id}`, {
        method: 'PATCH',
        body: form,
      });
      if (!r2.ok) throw new Error('Failed to upload project image');
      isDirtyAvatar.value = false;
    }

    const r3 = await authFetch('/api/v1/pm/project/users', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: project.value.id,
        users: projectUsers.value.map(u => ({ id: u.id, role: u.role })),
      }),
    });
    if (!r3.ok) throw new Error('Failed to update project users');

    const fresh = await (await authFetch(`/api/v1/pm/project?project_id=${encodeURIComponent(project.value.id)}`)).json();
    projectStore.setProjectInfo(fresh.id, fresh.name, fresh.description, fresh.color, fresh.img_url, fresh.type);

    notifySuccess('Project updated');
  } catch (e) {
    console.error(e);
    notifyError(e.message || 'Update failed');
  }
}

const showDelete = ref(false);

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


const showColorPicker = ref(false);
const customColor = ref(project.value.color);

function onColorChange(val) {
  if (val === 'custom') {
    showColorPicker.value = true;
  } else {
    project.value.color = val;
  }
}

function applyCustomColor() {
  project.value.color = customColor.value;
  showColorPicker.value = false;
}

async function deleteProject() {
  try {
    const res = await authFetch(
      `/api/v1/pm/project?project_id=${encodeURIComponent(project.value.id)}`,
      { method: 'DELETE' }
    );
    const body = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(body.message || 'Failed to delete project');

    notifySuccess('Project deleted');
    showDelete.value = false;
    projectStore.setProjectInfo(null, null, null, null, null, null);
    router.push('/projectslist');
  } catch (e) {
    console.error(e);
    notifyError(e.message || 'Delete failed');
  }
}

const showSnackbar = ref(false);
const snackbarMessage = ref('');
const snackbarColor = ref('green');

const notifySuccess = (msg) => {
  snackbarMessage.value = msg;
  snackbarColor.value = 'green';
  showSnackbar.value = true;
};

const notifyError = (msg) => {
  snackbarMessage.value = msg;
  snackbarColor.value = 'red';
  showSnackbar.value = true;
};

const isValid = computed(() => {

  console.log('Validating:', {
    name: project.value.name,
    description: project.value.description,
    type: project.value.type,
    color: project.value.color,
    users: projectUsers.value
  });

  return project.value.name.trim() &&
    project.value.description.trim() &&
    project.value.type &&
    projectUsers.value.length != 0 &&
    project.value.color
});
</script>

<style scoped>
.settings-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}

.project-avatar {
  border: 2px solid #555;
  font-size: 40px;
  background-color: #555;
}

.avatar-btn {
  margin-left: -35px;
  margin-top: 70px;
  background-color: #1e88e5;
  color: white;
  max-width: 36px;
  max-height: 36px;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.d-none {
  display: none;
}

.v-card {
  background-color: #1e1e1e;
  color: #ffffff;
}

.collaborator-row {
  display: flex;
  align-items: center;
}
</style>
