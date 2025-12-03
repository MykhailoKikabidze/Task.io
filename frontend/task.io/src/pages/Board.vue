<route lang="yaml">
  meta:
    layout: navigation
</route>

<template>
  <v-container class="board-container">
    <v-row class="mb-2 align-center">
      <v-col cols="12" md="8">
        <h2 class="text-h6 font-weight-bold">Project Board</h2>
        <div class="text-medium-emphasis text-caption">
          <template v-if="activeSprint">Active sprint: <strong>{{ activeSprint.name }}</strong> · {{
            activeSprint.start_date }} — {{ activeSprint.end_date || '…' }}</template>
          <template v-else>No active sprint</template>
        </div>
      </v-col>
      <v-col cols="12" md="4" class="d-flex justify-end gap-2">
        <v-btn v-if="activeSprint" color="blue" variant="elevated" size="small" @click="reloadAll" :loading="loading">
          Refresh
        </v-btn>
        <v-btn v-if="activeSprint && myRole <= 1" color="red" variant="elevated" size="small" @click="confirmFinish = true">
          Finish sprint
        </v-btn>
      </v-col>
    </v-row>

    <v-alert v-if="!loading && !activeSprint" type="info" border="start" variant="tonal" class="mb-4">
      There is no active sprint in this project. Start a sprint to see tasks here.
    </v-alert>

    <v-progress-linear v-if="loading" indeterminate color="blue" class="mb-4" />

    <v-row v-if="!loading && activeSprint">
      <v-col v-for="col in columnOrder" :key="col" cols="12" md="4">
        <v-card class="pa-3" elevation="8">
          <div class="d-flex align-center mb-1">
            <h3 class="text-subtitle-1 font-weight-medium mr-2">{{ col }}</h3>
            <v-chip size="x-small" color="blue" variant="tonal">{{ columns[col].length }}</v-chip>
          </div>
          <v-divider class="mb-2" />

          <div class="task-list">
            <v-empty-state v-if="!columns[col].length" headline="No tasks" class="py-6" />

            <v-list v-else density="compact">
              <v-list-item v-for="task in columns[col]" :key="task.id" class="mb-2">
                <v-card class="pa-3" color="grey-darken-3" elevation="2">
                  <div class="d-flex justify-space-between align-start">
                    <div class="mr-4" style="min-width:0">
                      <div class="text-subtitle-2 font-weight-medium text-truncate">{{ task.title }}</div>
                      <div class="text-caption text-medium-emphasis text-truncate-2">{{ task.description }}</div>
                      <div class="text-caption mt-1">
                        Type: {{ typeToLabel(task.type) }} • Priority: {{ task.priority }}
                      </div>


                      <div v-if="task._assignee" class="d-flex align-center mt-2">
                        <v-avatar size="20" class="mr-2">
                          <v-img :src="task._assignee.img_url || placeholderAvatar" />
                        </v-avatar>
                        <span class="text-caption">{{ task._assignee.name }} {{ task._assignee.surname }}</span>
                      </div>
                    </div>

                    <v-btn v-if="myRole <= 2" icon variant="text" color="blue" @click="openEdit(task)">
                      <v-icon icon="mdi-pencil"/>
                    </v-btn>
                  </div>
                </v-card>
              </v-list-item>
            </v-list>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="dlg.show" max-width="560">
      <v-card>
        <v-card-title class="text-h6">Edit task</v-card-title>
        <v-card-text>
          <v-text-field v-model="dlg.model.title" label="Title" prepend-inner-icon="mdi-format-title" density="compact"
            variant="outlined" />
          <v-textarea v-model="dlg.model.description" label="Description" rows="3" auto-grow
            prepend-inner-icon="mdi-text-box-outline" density="compact" variant="outlined" />

          <v-row>
            <v-col cols="12" md="6">
              <v-select v-model="dlg.model._typeLabel" :items="taskTypeLabels" label="Type"
                prepend-inner-icon="mdi-shape-outline" density="compact" variant="outlined" />
            </v-col>
            <v-col cols="12" md="6">
              <v-select v-model="dlg.model.priority" :items="priorityOptions" label="Priority"
                prepend-inner-icon="mdi-flag-outline" density="compact" variant="outlined" />
            </v-col>
          </v-row>

          <v-select v-model="dlg.model._statusLabel" :items="columnOrder" label="Status"
            prepend-inner-icon="mdi-format-list-bulleted" density="compact" variant="outlined" />

          <v-autocomplete :disabled="myRole >= 2" v-model="dlg.model._assigneeId" :items="assigneeItems" item-title="label" item-value="id"
            clearable label="Assignee" prepend-inner-icon="mdi-account" density="compact" variant="outlined">
            <template #item="{ props, item }">
              <v-list-item v-bind="props">
                <template #prepend>
                  <v-avatar size="22" class="mr-2"><v-img :src="item.raw.img_url || placeholderAvatar" /></v-avatar>
                </template>
                <template #title>
                  {{ item.raw.label }}
                </template>
                <template #subtitle>
                  {{ item.raw.email }}
                </template>
              </v-list-item>
            </template>
          </v-autocomplete>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="dlg.show = false">Cancel</v-btn>
          <v-btn color="blue" :disabled="!isValid" :loading="dlg.saving" @click="saveTask">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="confirmFinish" max-width="420">
      <v-card>
        <v-card-title class="text-h6">Finish sprint?</v-card-title>
        <v-card-text>Mark the current sprint as finished. Its end date will be set to today.</v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="confirmFinish = false">Cancel</v-btn>
          <v-btn color="red" :loading="finishing" @click="finishSprint">Finish</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="2000" location="bottom right">
      <div class="text-center w-100">{{ snackbar.msg }}</div>
      <template #actions>
        <v-btn variant="text" icon="mdi-close" @click="snackbar.show = false" />
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useProjectStore } from '@/stores/project'
import { useRouter } from 'vue-router'
import { authFetch } from '@/utils/authFetch'

const projectStore = useProjectStore()

const loading = ref(false)
const finishing = ref(false)
const confirmFinish = ref(false)
const router = useRouter()

let myRole = 3;

const activeSprint = ref(null)
const tasks = ref([])
const projectUsers = ref([])

const placeholderAvatar = '/src/assets/avatar.jpg'

const columnOrder = ['To Do', 'In Progress', 'Done']

const STATUS_DB_TO_UI = {
  'to do': 'To Do',
  'in progress': 'In Progress',
  'done': 'Done',
};
const STATUS_UI_TO_DB = Object.fromEntries(
  Object.entries(STATUS_DB_TO_UI).map(([db, ui]) => [ui, db])
);

const TYPE_DB_TO_UI = {
  design: 'Design',
  bug: 'Bug',
  feature: 'Feature',
  docs: 'Docs',
  refactor: 'Refactor',
  improvement: 'Improvement',
  'user story': 'User Story',
};
const TYPE_UI_TO_DB = Object.fromEntries(
  Object.entries(TYPE_DB_TO_UI).map(([db, ui]) => [ui, db])
);

const taskTypeLabels = Object.values(TYPE_DB_TO_UI);

const statusToLabel = (s) => STATUS_DB_TO_UI[String(s || '').toLowerCase()] || 'To Do';
const labelToStatus = (l) => STATUS_UI_TO_DB[l] || 'to do';
const typeToLabel = (t) => TYPE_DB_TO_UI[String(t || '').toLowerCase()] || 'Design';
const labelToType = (l) => TYPE_UI_TO_DB[l] || 'design';


const columns = reactive({ 'To Do': [], 'In Progress': [], 'Done': [] })

const taskTypes = ['Design', 'Bug', 'Feature', 'Docs', 'Refactor', 'Improvement', 'User Story']
const priorityOptions = Array.from({ length: 10 }, (_, i) => i + 1)

const assigneeItems = computed(() => projectUsers.value.map(u => ({
  id: u.id,
  label: `${u.name} ${u.surname}`,
  email: u.email,
  img_url: u.img_url,
})))

const dlg = reactive({
  show: false,
  saving: false,
  model: {},
  original: null,
})

const snackbar = reactive({ show: false, color: 'green', msg: '' })

function toast(ok, msg) {
  snackbar.show = true
  snackbar.color = ok ? 'green' : 'red'
  snackbar.msg = msg
}

onMounted(reloadAll)

async function reloadAll() {

  myRole = localStorage.getItem("currentProjectRole") || 3

  try {
    loading.value = true
    await loadActiveSprint()
    if (activeSprint.value) {
      await Promise.all([loadSprintTasks(activeSprint.value.id), loadProjectUsers(projectStore.getProjectInfo().id)])
      rebuildColumns()
    }
  } catch (e) {
    console.error(e)
    toast(false, 'Failed to load board')
  } finally {
    loading.value = false
  }
}

async function loadActiveSprint() {
  const pid = JSON.parse(localStorage.getItem("currentProject")).id
  const projectInfo = JSON.parse(localStorage.getItem("currentProject"))
  projectStore.setProjectInfo(projectInfo.id, projectInfo.name, projectInfo.type, projectInfo.description, projectInfo.color, projectInfo.avatar)

  if (!pid) router.push('/projectslist')
  const res = await authFetch(`/api/v1/pm/sprint/project/${encodeURIComponent(pid)}`)
  if (!res.ok) throw new Error('Failed to fetch sprints')
  const data = await res.json()
  activeSprint.value = (data.sprints || []).find(s => s.is_started) || null
}

async function loadSprintTasks(sprintId) {
  const res = await authFetch(`/api/v1/task/sprint/${encodeURIComponent(sprintId)}`)
  if (!res.ok) throw new Error('Failed to fetch sprint tasks')
  const data = await res.json()
  tasks.value = (data.tasks || []).map(t => ({
    ...t,
    _statusLabel: statusToLabel(t.status),
    _typeLabel: typeToLabel(t.type),
  }))
}

async function loadProjectUsers(projectId) {
  const res = await authFetch(`/api/v1/pm/project/users?project_id=${encodeURIComponent(projectId)}`)
  if (!res.ok) throw new Error('Failed to fetch project users')
  const data = await res.json()
  projectUsers.value = (data.users || []).map(u => ({
    id: u.id,
    name: u.name,
    surname: u.surname,
    email: u.email,
    img_url: u.img_url,
    role: u.role,
  }))
}

function rebuildColumns() {
  columns['To Do'] = [];
  columns['In Progress'] = [];
  columns['Done'] = [];
  for (const t of tasks.value) {
    const col = t._statusLabel;
    const ass = projectUsers.value.find(u => u.id === t.assigned_to) || null;
    columns[col].push({ ...t, _assignee: ass });
  }
}

function openEdit(task) {
  dlg.original = task;
  dlg.model = {
    ...task,
    _statusLabel: statusToLabel(task.status),
    _typeLabel:   typeToLabel(task.type),
    _assigneeId:  task.assigned_to || null,
  };
  dlg.show = true;
}

async function saveTask() {
  try {
    dlg.saving = true
    const payload = {
      id: dlg.model.id,
      title: dlg.model.title,
      description: dlg.model.description,
      priority: dlg.model.priority,
      type: labelToType(dlg.model._typeLabel),
      assigned_to: dlg.model._assigneeId || '',
      epic_id: dlg.model.epic_id || '',
      sprint_id: dlg.model.sprint_id,
      project_id: dlg.model.project_id,
      start_date: dlg.model.start_date,
      end_date: dlg.model.end_date,
      status: labelToStatus(dlg.model._statusLabel),
    }

    const res = await authFetch('/api/v1/task', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    if (!res.ok) throw new Error('Update failed')

    const idx = tasks.value.findIndex(t => t.id === dlg.model.id)
    if (idx !== -1) {
      tasks.value[idx] = { ...tasks.value[idx], ...payload, _statusLabel: dlg.model._statusLabel, assigned_to: payload.assigned_to }
    }
    rebuildColumns()

    toast(true, 'Task updated')
    dlg.show = false
  } catch (e) {
    console.error(e)
    toast(false, 'Could not update task')
  } finally {
    dlg.saving = false
  }
}

async function finishSprint() {
  try {
    finishing.value = true
    const today = new Date()
    const dd = String(today.getDate()).padStart(2, '0')
    const mm = String(today.getMonth() + 1).padStart(2, '0')
    const yyyy = today.getFullYear()
    const endStr = `${dd}.${mm}.${yyyy}`

    const payload = {
      id: activeSprint.value.id,
      name: activeSprint.value.name,
      description: activeSprint.value.description || '',
      start_date: activeSprint.value.start_date,
      end_date: endStr,
      is_started: false,
      project_id: activeSprint.value.project_id,
      tasks: [],
    }

    const res = await authFetch('/api/v1/pm/sprint', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) throw new Error('Failed to finish sprint')

    confirmFinish.value = false
    toast(true, 'Sprint finished')
    await reloadAll()
  } catch (e) {
    console.error(e)
    toast(false, 'Could not finish sprint')
  } finally {
    finishing.value = false
  }
}

const isValid = computed(() => {
  return dlg.model.title &&
    dlg.model.description
});
</script>

<style scoped>
.board-container {
  max-width: 1300px;
  margin: auto;
  padding-top: 16px;
}

.task-list {
  max-height: 64vh;
  overflow-y: auto;
}

.text-truncate-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.gap-2 {
  gap: 8px;
}
</style>
