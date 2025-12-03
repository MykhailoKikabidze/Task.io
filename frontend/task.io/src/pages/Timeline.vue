<route lang="yaml">
    meta:
      layout: navigation
</route>

<template>
    <v-container class="timeline-container">
        <v-card class="filters-card pa-4 mb-4" elevation="8">
            <v-row>
                <v-col cols="4">
                    <v-select v-model="selectedProject" :items="projectOptions" item-title="title" item-value="value"
                        label="Select Project" variant="outlined" density="compact" />
                </v-col>

                <v-col cols="4">
                    <v-select v-model="selectedTimeframe" :items="timeframes" label="Timeframe" variant="outlined"
                        density="compact" />
                </v-col>

                <v-col cols="4">
                    <v-select v-model="selectedAssign" :items="assignedOptions" item-title="title" item-value="value"
                        label="Assigned filter" variant="outlined" density="compact" />
                </v-col>
            </v-row>
        </v-card>

        <v-card class="gantt-card pa-4" elevation="8">
            <h4 class="mb-4">Gantt Chart</h4>

            <div class="time-scale">
                <div v-for="(label, index) in timeLabels" :key="index" class="time-label">
                    {{ label }}
                </div>
            </div>

            <div class="gantt-chart">
                <div class="gantt-row" v-for="(task, index) in filteredTasks" :key="index">
                    <v-tooltip location="bottom" open-on-hover>
                        <template #activator="{ props }">
                            <div v-bind="props" class="gantt-task" :style="getTaskStyle(task)">
                                <span class="task-label">{{ task.name }}</span>
                            </div>
                        </template>
                        <span class="tooltip-content">{{ getTaskTooltip(task) }}</span>
                    </v-tooltip>
                </div>
            </div>
        </v-card>
    </v-container>
</template>

<script setup>
import { ref, computed } from "vue";
import { format, addDays, startOfDay } from "date-fns";
import { authFetch } from "@/utils/authFetch";

const projectOptions = ref([{ title: 'All Projects', value: 'all' }]);
const selectedProject = ref('all');

const assignedOptions = [
    { title: 'All tasks', value: 'all' },
    { title: 'Assigned to me', value: 'me' },
];
const selectedAssign = ref('all');

const timeframes = ref(['Week', 'Month', 'Quarter']);
const selectedTimeframe = ref('Month');

const tasks = ref([]);
const currentDate = new Date();

function parseDdMmYyyy(s) {
    const [dd, mm, yyyy] = s.split('.');
    return new Date(`${yyyy}-${mm}-${dd}T00:00:00`);
}

function colorByProject(name) {
    const palette = ['#00bcd4', '#f44336', '#ffeb3b', '#4caf50', '#e91e63', '#3f51b5', '#009688', '#cddc39', '#ff9800', '#673ab7', '#795548', '#9c27b0', '#2196f3'];
    let hash = 0;
    for (let i = 0; i < name.length; i++) hash = (hash * 31 + name.charCodeAt(i)) >>> 0;
    return palette[hash % palette.length];
}

function mapApiTimeline(data) {
  const arr = Array.isArray(data) ? data : (data.items || data.timeline || []);
  return arr.map((t) => {
    const start =
      t.start_date ? parseDdMmYyyy(t.start_date) : startOfDay(new Date());

    const rawEnd =
      t.end_date ? parseDdMmYyyy(t.end_date)
      : t.sprint_end_date ? parseDdMmYyyy(t.sprint_end_date)
      : null;

    const name = t.task_name;
    const project = t.project_name;
    const color = seededColor(`${name}__${project}`);

    return {
      id: t.id || t.task_id || `${name}-${project}`,
      name,
      project,
      sprintId: t.sprint_id || t.sprintId || null,
      start,
      end: rawEnd,
      color,
    };
  });
}


const ACCESSIBLE_COLORS = [
  "#1b5e20","#2e7d32","#33691e","#004d40","#006064","#01579b","#0d47a1",
  "#1a237e","#283593","#303f9f","#3949ab","#3f51b5","#4527a0","#512da8",
  "#5e35b1","#6a1b9a","#7b1fa2","#8e24aa","#4a148c","#311b92","#263238",
  "#37474f","#455a64","#546e7a","#263238","#37474f","#2c3e50","#34495e",
  "#1f2d3d","#2d3436","#3e2723","#4e342e","#5d4037","#6d4c41","#795548",
  "#4a6572","#2b4c59","#264653","#2a9d8f","#1f7a8c","#1b4965"
];

function seededColor(seed) {
  let h = 2166136261;
  for (let i = 0; i < seed.length; i++) {
    h ^= seed.charCodeAt(i);
    h += (h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24);
  }
  const idx = Math.abs(h) % ACCESSIBLE_COLORS.length;
  return ACCESSIBLE_COLORS[idx];
}

async function fetchProjects() {
    const res = await authFetch('/api/v1/pm/me/projects');
    if (!res.ok) return;
    const data = await res.json();
    const items = (data.projects || []).map(p => ({ title: p.name, value: p.id }));
    projectOptions.value = [{ title: 'All Projects', value: 'all' }, ...items];
}

async function loadTimeline() {
  let url = '';
  const pid = selectedProject.value;

  if (pid === 'all' && selectedAssign.value === 'all') url = '/api/v1/analytics/timeline/all';
  else if (pid === 'all' && selectedAssign.value === 'me') url = '/api/v1/analytics/timeline/all/me';
  else if (pid !== 'all' && selectedAssign.value === 'all') url = `/api/v1/analytics/timeline/${pid}`;
  else url = `/api/v1/analytics/timeline/me/${pid}`;

  const res = await authFetch(url);
  if (!res.ok) { tasks.value = []; return; }
  const json = await res.json();
  tasks.value = mapApiTimeline(json);
  await finalizeTaskDates();
}

const sprintEndById = ref({});

async function loadProjectSprints(projectId) {
  const res = await authFetch(`/api/v1/pm/sprint/project/${encodeURIComponent(projectId)}`);
  if (!res.ok) return;
  const json = await res.json();
  const map = {};
  (json.sprints || []).forEach((s) => {
    if (s?.id && s?.end_date) map[s.id] = parseDdMmYyyy(s.end_date);
  });
  sprintEndById.value = { ...sprintEndById.value, ...map };
}

let loadedAllSprints = false;
async function ensureSprintEndsLoaded() {
  if (selectedProject.value === 'all') {
    if (loadedAllSprints) return;
    const ids = projectOptions.value.filter(p => p.value !== 'all').map(p => p.value);
    await Promise.all(ids.map((id) => loadProjectSprints(id)));
    loadedAllSprints = true;
  } else {
    await loadProjectSprints(String(selectedProject.value));
  }
}

async function finalizeTaskDates() {
  const needSprintEnd = tasks.value.some(t => !t.end && t.sprintId);
  if (needSprintEnd) await ensureSprintEndsLoaded();

  tasks.value = tasks.value.map(t => {
    if (!t.end) {
      const sprintEnd = t.sprintId ? sprintEndById.value[t.sprintId] : null;
      t.end = sprintEnd || addDays(t.start, 1);
    }
    return t;
  });
}

onMounted(async () => {
    await fetchProjects();
    await loadTimeline();
});
watch([selectedProject, selectedAssign], () => loadTimeline());

const timeLabels = computed(() => {
    const timeframe = selectedTimeframe.value;
    const labels = [];
    let interval = 1;
    let totalDays = 7;

    if (timeframe === "Week") {
        interval = 1;
        totalDays = 7;
    } else if (timeframe === "Month") {
        interval = 2;
        totalDays = 30;
    } else if (timeframe === "Quarter") {
        interval = 10;
        totalDays = 90;
    }

    for (let i = 0; i <= totalDays; i += interval) {
        const labelDate = addDays(currentDate, i);
        labels.push(format(labelDate, "MM/dd"));
    }

    return labels;
});

const filteredTasks = computed(() => {
  const currDate = startOfDay(new Date());

  const ready_tasks = tasks.value
    .map(t => ({
      ...t,
      start: startOfDay(new Date(t.start)),
      end: startOfDay(new Date(t.end)),
    }))
    .filter(t => t.end > currDate);

  return ready_tasks;
});

const getTaskStyle = (task) => {
    const startDate = new Date(task.start);
    const endDate = new Date(task.end);
    const totalDays = (endDate - startDate) / (1000 * 60 * 60 * 24);

    const scale = selectedTimeframe.value === "Week" ? 7 : selectedTimeframe.value === "Month" ? 30 : 90;

    const startPercentage = ((startDate - currentDate) / (1000 * 60 * 60 * 24)) / scale * 100;
    const widthPercentage = (totalDays / scale) * 100;

    return {
        backgroundColor: task.color,
        left: `${startPercentage}%`,
        width: `${widthPercentage}%`,
        transition: "all 0.3s ease",
    };
};

const getTaskTooltip = (task) => {
    const start = format(task.start, 'MM/dd/yyyy');
    const end = format(task.end, 'MM/dd/yyyy');
    return `Task: ${task.name}\nProject: ${task.project}\nFrom: ${start} - To: ${end}`;
};
</script>

<style scoped>
.timeline-container {
    max-width: 1300px;
    margin: auto;
    padding-top: 20px;
}

.filters-card {
    background-color: #1e1e1e;
}

.gantt-card {
    background-color: #1e1e1e;
    height: 530px;
    overflow: hidden;
    position: relative;
}

.time-scale {
    display: flex;
    justify-content: space-between;
    padding-bottom: 8px;
    border-bottom: 1px solid #333;
    margin-bottom: 10px;
    color: #888;
    font-size: 12px;
}

.time-label {
    width: calc(100% / 8);
    text-align: center;
}

.gantt-chart {
    position: relative;
    height: 430px;
    overflow-y: auto;
    overflow-x: hidden;
}

.gantt-row {
    position: relative;
    height: 50px;
    border-bottom: 1px solid #333;
    display: flex;
    align-items: center;
}

.gantt-task {
  position: absolute;
  height: 30px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  padding: 0 8px;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  z-index: 1;
  text-shadow: 0 1px 2px rgba(0,0,0,.5);
}

.task-label {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  width: 100%;
  pointer-events: none;
}


.tooltip-content {
    white-space: pre-line;
}
</style>