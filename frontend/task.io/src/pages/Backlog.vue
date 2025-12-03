<route lang="yaml">
  meta:
    layout: navigation
</route>

<template>
  <v-container class="backlog-container">
    <v-row class="mb-4 justify-center">
      <v-col cols="12">
        <h2 class="text-h5 font-weight-bold text-center">Backlog</h2>
        <p class="text-subtitle-1 text-medium-emphasis text-center">
          Manage tasks, sprints and epics
        </p>
      </v-col>
    </v-row>

    <v-row class="justify-center">
      <v-col cols="12" md="6">
        <v-card class="pa-3" elevation="20">
          <v-card-title class="text-h6">{{ currentTitle }}</v-card-title>
          <v-divider class="mb-2" />

          <v-row class="mb-4 ml-2 mr-2">
            <v-col cols="12">
              <v-select v-model="sortBy" :items="sortOptions" label="Sort by" density="compact" variant="outlined"
                hide-details />
            </v-col>
          </v-row>

          <div class="list-container">
            <v-list density="compact">
              <v-list-item v-for="(item, idx) in sortedList" :key="item._key"
                :class="['mb-2', { 'selected-row': selectedIdx === indexMap[idx] }]" @click="selectItem(indexMap[idx])">
                <v-card class="pa-2 w-100 d-flex justify-space-between" color="grey-darken-3" elevation="2">
                  <div>
                    <div class="text-subtitle-2 font-weight-medium">{{ displayTitle(item) }}</div>
                    <div class="text-caption text-medium-emphasis">{{ item.description }}</div>

                    <div v-if="view === 'tasks'" class="text-caption">
                      Type: {{ prettyType(item.type) }} • Priority: {{ item.priority }}
                      • Start: {{ fromApiDate(item.start_date) || '—' }}
                      • Due: {{ fromApiDate(item.end_date) || '—' }}
                    </div>

                    <div v-else-if="view === 'sprints'" class="text-caption">
                      Start: {{ fromApiDate(item.start_date) || '—' }}
                      • End: {{ fromApiDate(item.end_date) || '—' }}
                      • Started: {{ item.is_started ? 'Yes' : 'No' }}
                    </div>

                    <div v-else class="text-caption">
                      Priority: {{ item.priority }}
                      • Start: {{ fromApiDate(item.start_date) || '—' }}
                      • End: {{ fromApiDate(item.end_date) || '—' }}
                    </div>
                  </div>
                </v-card>
              </v-list-item>
            </v-list>
          </div>

          <v-btn color="blue" block class="mt-6 fixed-btn" @click="openAddDialog" :disabled="myRole >= 2">
            ADD {{ currentTitle.toUpperCase() }}
          </v-btn>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card class="pa-3 mb-4" elevation="20">
          <v-card-title class="text-h6">Edit {{ currentTitle.slice(0, -1) }}</v-card-title>
          <v-divider class="mb-2" />

          <v-text-field v-model="draftTitle" :label="view === 'tasks' ? 'Title *' : 'Name *'"
            :disabled="!itemSelected || myRole >= 2" density="compact" variant="outlined" />
          <v-textarea v-model="draft.description" label="Description *" rows="4"
            :disabled="!itemSelected || myRole >= 2" density="compact" variant="outlined" />

          <template v-if="view === 'tasks'">
            <v-select v-model="draft.type" :items="taskTypeOptionsUI" label="Type *"
              :disabled="!itemSelected || myRole >= 2" density="compact" variant="outlined" :item-title="t => t"
              :item-value="t => toTypeDB(t)" :return-object="false" />
            <v-select v-model="draft.priority" :items="priorityOptions" label="Priority *"
              :disabled="!itemSelected || myRole >= 2" density="compact" variant="outlined" />
            <v-text-field v-model="draft.start_date_iso" label="Start Date" type="date"
              :disabled="!itemSelected || myRole >= 2" density="compact" variant="outlined" />
            <v-text-field v-model="draft.end_date_iso" label="Due Date" type="date"
              :disabled="!itemSelected || myRole >= 2" density="compact" variant="outlined" />

            <v-autocomplete v-model="draft.assigned_to" :items="assigneeItems" item-title="label" item-value="id"
              clearable label="Assignee" :disabled="!itemSelected || myRole >= 2" density="compact" variant="outlined">
              <template #item="{ props, item }">
                <v-list-item v-bind="props">
                  <template #prepend>
                    <v-avatar size="22" class="mr-2"><v-img :src="item.raw.img_url || placeholderUser" /></v-avatar>
                  </template>
                  <template #title>{{ item.raw.label }}</template>
                  <template #subtitle>{{ item.raw.email }}</template>
                </v-list-item>
              </template>
            </v-autocomplete>
          </template>

          <template v-else-if="view === 'sprints'">
            <v-text-field v-model="draft.start_date_iso" label="Start Date" type="date"
              :disabled="!itemSelected || myRole >= 2" density="compact" variant="outlined" />
            <v-text-field v-model="draft.end_date_iso" label="End Date" type="date"
              :disabled="!itemSelected || myRole >= 2" density="compact" variant="outlined" />

            <v-autocomplete :key="sprintPickerKey" v-model="draft.taskIds" :items="availableTasksForCurrentSprint"
              item-title="title" item-value="id" :return-object="false" chips multiple clearable label="Sprint tasks"
              :disabled="!itemSelected || myRole >= 2" density="compact" variant="outlined" />
          </template>

          <template v-else>
            <v-select v-model="draft.priority" :items="priorityOptions" label="Priority *"
              :disabled="!itemSelected || myRole >= 2" density="compact" variant="outlined" />
            <v-text-field v-model="draft.start_date_iso" label="Start Date" type="date"
              :disabled="!itemSelected || myRole >= 2" density="compact" variant="outlined" />
            <v-text-field v-model="draft.end_date_iso" label="End Date" type="date"
              :disabled="!itemSelected || myRole >= 2" density="compact" variant="outlined" />

            <v-autocomplete :key="epicPickerKey" v-model="draft.taskIds" :items="availableTasksForCurrentEpic"
              item-title="title" item-value="id" :return-object="false" chips multiple clearable label="User stories"
              :disabled="!itemSelected || myRole >= 2" density="compact" variant="outlined" />
          </template>

          <v-btn v-if="view === 'sprints' && itemSelected && myRole < 2"
            :disabled="!draft.name || !draft.description || !draft.end_date_iso" color="green" block class="mb-2"
            @click="startSprint">
            START SPRINT
          </v-btn>

          <v-btn color="blue" block class="mb-2" v-if="myRole < 2"
            :disabled="!itemSelected || myRole >= 2 || !(draftTitle && draftTitle.trim()) || !(draft.description && draft.description.trim())"
            @click="saveDraft">
            SAVE
          </v-btn>



          <v-btn color="red" block v-if="myRole < 2" :disabled="!itemSelected || myRole >= 2" @click="deleteItem">
            DELETE
          </v-btn>
        </v-card>

        <v-card class="pa-3" elevation="20">
          <v-card-title class="text-h6">View options</v-card-title>
          <v-divider class="mb-2" />
          <v-radio-group v-model="view" @update:model-value="clearSelection">
            <v-radio label="Tasks" value="tasks" />
            <v-radio label="Sprints" value="sprints" />
            <v-radio label="Epics" value="epics" />
          </v-radio-group>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="dialog.task" max-width="560" persistent>
      <v-card>
        <v-card-title>Create task</v-card-title>
        <v-card-text>
          <v-text-field v-model="newTask.title" label="Title *" prepend-inner-icon="mdi-format-title" density="compact"
            variant="outlined" required />
          <v-textarea v-model="newTask.description" label="Description *" rows="3"
            prepend-inner-icon="mdi-text-box-outline" density="compact" variant="outlined" />
          <v-select v-model="newTask.type" :items="taskTypeOptionsUI" label="Type *" :item-title="t => t"
            :item-value="t => toTypeDB(t)" density="compact" variant="outlined" />
          <v-select v-model="newTask.priority" :items="priorityOptions" label="Priority *" density="compact"
            variant="outlined" />
          <v-text-field v-model="newTask.start_date_iso" label="Start Date" type="date" density="compact"
            variant="outlined" />
          <v-text-field v-model="newTask.end_date_iso" label="Due Date" type="date" density="compact"
            variant="outlined" />
          <v-autocomplete v-model="newTask.assigned_to" :items="assigneeItems" item-title="label" item-value="id"
            clearable label="Assignee" density="compact" variant="outlined" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="closeDialogs">Cancel</v-btn>
          <v-btn color="primary" :disabled="!newTask.title.trim() || !newTask.description.trim()"
            @click="addTask">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="dialog.sprint" max-width="640" persistent>
      <v-card>
        <v-card-title>Create sprint</v-card-title>
        <v-card-text>
          <v-text-field v-model="newSprint.title" label="Sprint name *" prepend-inner-icon="mdi-format-title"
            density="compact" variant="outlined" />
          <v-textarea v-model="newSprint.description" label="Goal / description *" rows="3"
            prepend-inner-icon="mdi-text-box-outline" density="compact" variant="outlined" />
          <v-text-field v-model="newSprint.start_date_iso" label="Start Date" type="date" density="compact"
            variant="outlined" />
          <v-text-field v-model="newSprint.end_date_iso" label="End Date" type="date" density="compact"
            variant="outlined" />
          <v-autocomplete v-model="newSprint.tasks" :items="tasksUnassignedToSprint" item-title="title" item-value="id"
            chips multiple return-object label="Add tasks" density="compact" variant="outlined" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="closeDialogs">Cancel</v-btn>
          <v-btn color="primary" :disabled="!newSprint.title.trim() || !newSprint.description.trim()"
            @click="addSprint">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="dialog.epic" max-width="640" persistent>
      <v-card>
        <v-card-title>Create epic</v-card-title>
        <v-card-text>
          <v-text-field v-model="newEpic.title" label="Epic name *" prepend-inner-icon="mdi-format-title"
            density="compact" variant="outlined" />
          <v-textarea v-model="newEpic.description" label="Description *" rows="3"
            prepend-inner-icon="mdi-text-box-outline" density="compact" variant="outlined" />
          <v-select v-model="newEpic.priority" :items="priorityOptions" label="Priority *" density="compact"
            variant="outlined" />
          <v-text-field v-model="newEpic.start_date_iso" label="Start Date" type="date" density="compact"
            variant="outlined" />
          <v-text-field v-model="newEpic.end_date_iso" label="End Date" type="date" density="compact"
            variant="outlined" />
          <v-autocomplete v-model="newEpic.tasks" :items="tasksUnassignedToEpic" item-title="title" item-value="id"
            chips multiple return-object label="Add tasks" density="compact" variant="outlined" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="closeDialogs">Cancel</v-btn>
          <v-btn color="primary" :disabled="!newEpic.title.trim() || !newEpic.description.trim()"
            @click="addEpic">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="sb.show" :timeout="2200" :color="sb.color" location="bottom right" elevation="4">
      <div class="w-100 text-center">{{ sb.text }}</div>
      <template #actions><v-btn icon variant="text"
          @click="sb.show = false"><v-icon>mdi-close</v-icon></v-btn></template>
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, Ref, reactive, computed, watch, onMounted } from 'vue'
import { useProjectStore } from '@/stores/project'
import { useAuthStore } from '@/stores/auth'
import { authFetch } from '@/utils/authFetch'

const toApiDate = (iso?: string) => iso ? iso.split('-').reverse().join('.') : ''
const fromApiDate = (api?: string) => {
  if (!api) return ''
  const [dd, mm, yyyy] = api.split('.')
  return `${yyyy}-${mm}-${dd}`
}
const cap = (s: string) => s ? s[0].toUpperCase() + s.slice(1) : ''
const prettyType = (t?: string) => (t || '').split(' ').map(cap).join(' ')
const toTypeDB = (label: string) => (label || '').toLowerCase()
const displayTitle = (it: any) => it?.title ?? it?.name ?? ''

const projectStore = useProjectStore()
const authStore = useAuthStore()
const projectId = computed(() => JSON.parse(localStorage.getItem("currentProject")).id || '')
let myRole: Ref<number> = ref(
  Number(localStorage.getItem("currentProjectRole")) || 3
)

const lists = reactive({
  tasks: [] as any[],
  sprints: [] as any[],
  epics: [] as any[],
})

const projectUsers = ref<any[]>([])
const placeholderUser = '/src/assets/avatar.jpg'
const assigneeItems = computed(() => projectUsers.value.map(u => ({
  id: u.id, label: `${u.name} ${u.surname}`, email: u.email, img_url: u.img_url
})))
async function loadProjectUsers() {
  const res = await authFetch(`/api/v1/pm/project/users?project_id=${encodeURIComponent(projectId.value)}`)
  if (res.ok) {
    const data = await res.json()
    projectUsers.value = data.users || []
  }
}

async function fetchSprintTaskIds(id: string): Promise<string[]> {
  const res = await authFetch(`/api/v1/task/sprint/${encodeURIComponent(id)}`)
  if (!res.ok) return []
  const data = await res.json()
  return (data.tasks || []).map((t: any) => t.id)
}

async function fetchEpicTaskIds(id: string): Promise<string[]> {
  const res = await authFetch(`/api/v1/task/epic/${encodeURIComponent(id)}`)
  if (!res.ok) return []
  const data = await res.json()
  return (data.tasks || []).map((t: any) => t.id)
}

const pickerTick = ref(0)
const sprintPickerKey = computed(() => `sprint-${draft.id || 'none'}-${pickerTick.value}`)
const epicPickerKey = computed(() => `epic-${draft.id || 'none'}-${pickerTick.value}`)

const tasksVersion = ref(0)

async function loadTasks() {
  const res = await authFetch(`/api/v1/task/project/${encodeURIComponent(projectId.value)}`)
  if (!res.ok) throw new Error('tasks failed')
  const data = await res.json()
  lists.tasks = (data.tasks || []).map((t: any) => ({ ...t, _key: t.id }))
  tasksVersion.value++
}

async function loadSprints() {
  const res = await authFetch(`/api/v1/pm/sprint/project/${encodeURIComponent(projectId.value)}`)
  if (!res.ok) throw new Error('sprints failed')
  const data = await res.json()
  lists.sprints = (data.sprints || []).map((s: any) => ({ ...s, _key: s.id }))
}
async function loadEpics() {
  const res = await authFetch(`/api/v1/pm/epic/project/${encodeURIComponent(projectId.value)}`)
  if (!res.ok) throw new Error('epics failed')
  const data = await res.json()
  lists.epics = (data.epics || []).map((e: any) => ({ ...e, _key: e.id }))
}

async function reloadAll() {
  await Promise.all([loadTasks(), loadSprints(), loadEpics(), loadProjectUsers()])
}

const view = ref<'tasks' | 'sprints' | 'epics'>('tasks')
const taskTypeOptionsUI = ['Design', 'Bug', 'Feature', 'Docs', 'Refactor', 'Improvement', 'User Story']
const priorityOptions = Array.from({ length: 10 }, (_, i) => i + 1)
const placeholder = { title: '', description: '' }
const draftTitle = computed<string>({
  get() {
    return view.value === 'tasks' ? (draft.title || '') : (draft.name || '')
  },
  set(v: string) {
    if (view.value === 'tasks') draft.title = v
    else draft.name = v
  }
})


const currentList = computed(() => lists[view.value])
const currentTitle = computed(() => view.value.charAt(0).toUpperCase() + view.value.slice(1))
const sortBy = ref('Date')
const sortOptions = computed(() => view.value === 'tasks' ? ['Date', 'Type', 'Priority'] : view.value === 'sprints' ? ['Date'] : ['Date', 'Priority'])

const indexMap = ref<number[]>([])
const sortedList = computed(() => {
  const arr = currentList.value.map((v: any, i: number) => ({ item: v, idx: i }))
  let sorted = [...arr]
  if (sortBy.value === 'Date') {
    sorted.sort((a, b) => {
      const da = new Date(fromApiDate(a.item.end_date) || fromApiDate(a.item.start_date) || 0)
      const db = new Date(fromApiDate(b.item.end_date) || fromApiDate(b.item.start_date) || 0)
      return da.getTime() - db.getTime()
    })
  } else if (sortBy.value === 'Type' && view.value === 'tasks') {
    sorted.sort((a, b) => (a.item.type || '').localeCompare(b.item.type || ''))
  } else if (sortBy.value === 'Priority') {
    sorted.sort((a, b) => (b.item.priority || 0) - (a.item.priority || 0))
  }
  indexMap.value = sorted.map(x => x.idx)
  return sorted.map(x => x.item)
})

const selectedIdx = ref<number | null>(null)
const itemSelected = computed(() => selectedIdx.value !== null)
const draft = reactive<any>({ title: '', description: '', taskIds: [] as string[] })

async function selectItem(i: number) {
  selectedIdx.value = i
  const src: any = currentList.value[i]
  Object.assign(draft, JSON.parse(JSON.stringify(src)))

  draft.start_date_iso = fromApiDate(draft.start_date)
  draft.end_date_iso = fromApiDate(draft.end_date)

  if (view.value === 'sprints') {
    draft.taskIds = await fetchSprintTaskIds(src.id)
  } else if (view.value === 'epics') {
    draft.taskIds = await fetchEpicTaskIds(src.id)
  } else {
    draft.taskIds = []
  }
  pickerTick.value++
}


function clearSelection() {
  selectedIdx.value = null
  Object.assign(draft, { title: '', description: '', taskIds: [], start_date_iso: '', end_date_iso: '' })
  if (view.value === 'tasks') {
    Object.assign(draft, { type: '', priority: 1, assigned_to: '' })
  } else if (view.value === 'sprints') {
    Object.assign(draft, { name: '', start_date_iso: '', end_date_iso: '' })
  } else {
    Object.assign(draft, { name: '', priority: 1, start_date_iso: '', end_date_iso: '' })
  }
}

watch([() => draft.id, () => view.value], async () => {
  if (!itemSelected.value) return
  if (view.value === 'sprints') {
    draft.taskIds = await fetchSprintTaskIds(draft.id)
    pickerTick.value++
  } else if (view.value === 'epics') {
    draft.taskIds = await fetchEpicTaskIds(draft.id)
    pickerTick.value++
  }
})


const tasksUnassignedToSprint = computed(() => lists.tasks.filter(t => !t.sprint_id))
const tasksUnassignedToEpic = computed(() => lists.tasks.filter(t => !t.epic_id))
const availableTasksForCurrentSprint = computed(() => {
  if (!itemSelected.value) return []
  const cur = draft.id
  return lists.tasks.filter(t => !t.sprint_id || t.sprint_id === cur)
})
const availableTasksForCurrentEpic = computed(() => {
  if (!itemSelected.value) return []
  const cur = draft.id
  return lists.tasks.filter(t => !t.epic_id || t.epic_id === cur)
})

const dialog = reactive({ task: false, sprint: false, epic: false })
const newTask = reactive<any>({ title: '', description: '', type: toTypeDB('Design'), priority: 1, start_date_iso: '', end_date_iso: '', assigned_to: '' })
const newSprint = reactive<any>({ title: '', description: '', start_date_iso: '', end_date_iso: '', tasks: [] as any[] })
const newEpic = reactive<any>({ title: '', description: '', priority: 1, start_date_iso: '', end_date_iso: '', tasks: [] as any[] })
function openAddDialog() {
  dialog[view.value === 'tasks' ? 'task' : view.value === 'sprints' ? 'sprint' : 'epic'] = true
}
function closeDialogs() {
  dialog.task = dialog.sprint = dialog.epic = false
  Object.assign(newTask, { title: '', description: '', type: toTypeDB('Design'), priority: 1, start_date_iso: '', end_date_iso: '', assigned_to: '' })
  Object.assign(newSprint, { title: '', description: '', start_date_iso: '', end_date_iso: '', tasks: [] })
  Object.assign(newEpic, { title: '', description: '', priority: 1, start_date_iso: '', end_date_iso: '', tasks: [] })
}

async function addTask() {
  try {
    const payload = {
      title: newTask.title,
      description: newTask.description || '',
      priority: Number(newTask.priority) || 1,
      type: toTypeDB(newTask.type),
      assigned_to: newTask.assigned_to || '',
      epic_id: '',
      sprint_id: '',
      project_id: projectId.value,
      start_date: toApiDate(newTask.start_date_iso),
      end_date: toApiDate(newTask.end_date_iso),
      status: 'to do',
    }
    const res = await authFetch('/api/v1/task', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
    if (!res.ok) throw new Error('Create failed')
    await loadTasks()
    closeDialogs()
    toast(true, 'Task created')
  } catch (e) {
    console.error(e); toast(false, 'Could not create task')
  }
}

async function saveTask() {
  const src = currentList.value[selectedIdx.value as number]
  const payload = {
    id: draft.id,
    title: draft.title,
    description: draft.description || '',
    priority: Number(draft.priority) || 1,
    type: toTypeDB(draft.type || src.type),
    assigned_to: draft.assigned_to || '',
    epic_id: src.epic_id || '',
    sprint_id: src.sprint_id || '',
    project_id: projectId.value,
    start_date: toApiDate(draft.start_date_iso),
    end_date: toApiDate(draft.end_date_iso),
    status: 'to do',
  }
  const res = await authFetch('/api/v1/task', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
  if (!res.ok) throw new Error('Update failed')
}

async function deleteTask(id: string) {
  const res = await authFetch(`/api/v1/task/${encodeURIComponent(id)}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Delete failed')
}

function extractIds(arr: any[]) { return (arr || []).map((t: any) => t?.id ?? t) }

async function addSprint() {
  try {
    const payload = {
      name: newSprint.title,
      description: newSprint.description || '',
      start_date: toApiDate(newSprint.start_date_iso),
      end_date: toApiDate(newSprint.end_date_iso),
      is_started: false,
      project_id: projectId.value,
      tasks: (newSprint.tasks || []).map((t: any) => t.id),
    }
    const res = await authFetch('/api/v1/pm/sprint', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (!res.ok) throw new Error('Create sprint failed')

    await Promise.all([loadSprints(), loadTasks()])
    closeDialogs()
    toast(true, 'Sprint created')
  } catch (e) {
    console.error(e); toast(false, 'Could not create sprint')
  }
}


async function saveSprint() {
  const payload = {
    id: draft.id,
    name: draft.name || draft.title,
    description: draft.description || '',
    start_date: toApiDate(draft.start_date_iso),
    end_date: toApiDate(draft.end_date_iso),
    is_started: !!draft.is_started,
    project_id: projectId.value,
    tasks: draft.taskIds,
  }
  const res = await authFetch('/api/v1/pm/sprint', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
  if (!res.ok) throw new Error('Update sprint failed')

  await Promise.all([loadSprints(), loadTasks()])
  if (itemSelected.value && view.value === 'sprints') {
    draft.taskIds = await fetchSprintTaskIds(draft.id)
    pickerTick.value++
  }
}


async function deleteSprint(id: string) {
  const res = await authFetch(`/api/v1/pm/sprint/${encodeURIComponent(id)}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Delete sprint failed')
}

async function addEpic() {
  try {
    const payload = {
      name: newEpic.title,
      description: newEpic.description || '',
      priority: Number(newEpic.priority) || 1,
      start_date: toApiDate(newEpic.start_date_iso),
      end_date: toApiDate(newEpic.end_date_iso),
      project_id: projectId.value,
      tasks: (newEpic.tasks || []).map((t: any) => t.id),
    }
    const res = await authFetch('/api/v1/pm/epic', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (!res.ok) throw new Error('Create epic failed')

    await Promise.all([loadEpics(), loadTasks()])
    closeDialogs()
    toast(true, 'Epic created')
  } catch (e) {
    console.error(e); toast(false, 'Could not create epic')
  }
}


async function saveEpic() {
  const payload = {
    id: draft.id,
    name: draft.name || draft.title,
    description: draft.description || '',
    priority: Number(draft.priority) || 1,
    start_date: toApiDate(draft.start_date_iso),
    end_date: toApiDate(draft.end_date_iso),
    project_id: projectId.value,
    tasks: draft.taskIds,
  }
  const res = await authFetch('/api/v1/pm/epic', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
  if (!res.ok) throw new Error('Update epic failed')

  await Promise.all([loadEpics(), loadTasks()])
  if (itemSelected.value && view.value === 'epics') {
    draft.taskIds = await fetchEpicTaskIds(draft.id)
    pickerTick.value++
  }
}

async function deleteEpic(id: string) {
  const res = await authFetch(`/api/v1/pm/epic/${encodeURIComponent(id)}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Delete epic failed')
}

async function saveDraft() {
  try {
    if (view.value === 'tasks') await saveTask()
    else if (view.value === 'sprints') await saveSprint()
    else await saveEpic()

    await Promise.all([loadTasks(), loadSprints(), loadEpics()])
    toast(true, 'Saved')
    clearSelection()
  } catch (e) {
    console.error(e); toast(false, 'Save failed')
  }
}

async function deleteItem() {
  try {
    const id = (currentList.value[selectedIdx.value as number]).id
    if (view.value === 'tasks') await deleteTask(id)
    else if (view.value === 'sprints') await deleteSprint(id)
    else await deleteEpic(id)

    await Promise.all([loadTasks(), loadSprints(), loadEpics()])
    toast(true, 'Deleted')
    clearSelection()
  } catch (e) {
    console.error(e); toast(false, 'Delete failed')
  }
}

async function startSprint() {
  await loadSprints()
  const anotherActive = lists.sprints.find(s => s.is_started && s.id !== draft.id)
  if (anotherActive) { toast(false, 'Another active sprint already exists'); return }

  const payload = {
    id: draft.id,
    name: draft.name || draft.title,
    description: draft.description || '',
    start_date: toApiDate(draft.start_date_iso) || toApiDate(new Date().toISOString().slice(0, 10)),
    end_date: toApiDate(draft.end_date_iso),
    is_started: true,
    project_id: projectId.value,
    tasks: draft.taskIds,
  }
  const res = await authFetch('/api/v1/pm/sprint', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
  if (!res.ok) throw new Error('Start sprint failed')

  await loadSprints()
  draft.taskIds = await fetchSprintTaskIds(draft.id)
  pickerTick.value++
}

const sb = ref({ show: false, text: '', color: 'green' })
function toast(ok: boolean, text: string) { sb.value = { show: true, text, color: ok ? 'green' : 'red' } }

onMounted(reloadAll)
watch(view, clearSelection)
</script>

<style scoped>
.backlog-container {
  max-width: 1600px;
}

.list-container {
  overflow-y: auto;
  scrollbar-width: thin;
  max-height: 380px;
}

.list-container::-webkit-scrollbar {
  width: 8px;
}

.fixed-btn {
  margin-top: 24px;
}

.selected-row>.v-card {
  border: 2px solid #1e88e5;
}
</style>
