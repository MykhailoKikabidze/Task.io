<route lang="yaml">
    meta:
      layout: navigation
  </route>

<template>
  <v-container class="analytics-container">
    <v-card class="filters-card pa-4 mb-4" elevation="8">
      <v-row>
        <v-col cols="12" md="6">
          <v-select v-model="selectedProjectId" :items="projectItems" item-title="name" item-value="id"
            label="Select Project" variant="outlined" density="compact" />
        </v-col>

        <v-col cols="12" md="6">
          <v-select v-model="selectedAnalytics" :items="analyticsOptions" label="Select Analytics" variant="outlined"
            density="compact" />
        </v-col>
      </v-row>
    </v-card>


    <v-card class="chart-card pa-4" elevation="8">
      <h4 class="mb-4">Analytics Chart</h4>
      <v-container>
        <v-row>
          <v-col>
            <Bar :data="chartData" :options="chartOptions" />
          </v-col>
        </v-row>
      </v-container>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue";
import { Bar } from "vue-chartjs";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { authFetch } from "@/utils/authFetch";

ChartJS.register(BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

const analyticsOptions = [
  "Tasks Completed by User",
  "Tasks in Sprint (Completed / In Progress)",
  "Task Progress by Day",
];

const selectedAnalytics = ref(analyticsOptions[0]);

const projectItems = ref([]);
const selectedProjectId = ref(null);

async function loadMyProjects() {
  const res = await authFetch("/api/v1/pm/me/projects");
  if (!res.ok) { projectItems.value = []; return; }
  const data = await res.json();
  projectItems.value = (data.projects || []).map(p => ({ id: p.id, name: p.name }));
  if (!selectedProjectId.value && projectItems.value.length) {
    selectedProjectId.value = JSON.parse(localStorage.getItem("currentProject")).id;
    if (!selectedProjectId.value) {
        selectedProjectId.value = projectItems.value[0].id;
    }
  }
}

const completedByUser = ref([]);   
const sprintStatus    = ref([]);    
const progressByDay   = ref([]);     

async function fetchCompletedByUser(pid) {
  const r = await authFetch(`/api/v1/analytics/tasks/completed-by-user/${pid}`);
  completedByUser.value = r.ok ? await r.json() : [];
}

async function fetchSprintsStatus(pid) {
  const r = await authFetch(`/api/v1/analytics/sprints/task-status/${pid}`);
  sprintStatus.value = r.ok ? await r.json() : [];
}

async function fetchProgressByDay(pid) {
  const r = await authFetch(`/api/v1/analytics/tasks/progress-by-day/${pid}`);
  const data = r.ok ? await r.json() : [];

  const days = Array.isArray(data) ? data : (data.tasks || []);
  progressByDay.value = days;
}


async function loadCurrentAnalytics() {
  const pid = selectedProjectId.value;
  if (!pid) return;

  if (selectedAnalytics.value === "Tasks Completed by User") {
    await fetchCompletedByUser(pid);
  } else if (selectedAnalytics.value === "Tasks in Sprint (Completed / In Progress)") {
    await fetchSprintsStatus(pid);
  } else {
    await fetchProgressByDay(pid);
  }
}

watch([selectedProjectId, selectedAnalytics], loadCurrentAnalytics, { immediate: true });
onMounted(loadMyProjects);

const tooltipPayload = ref({
  completedByUser: [],          
  sprintsCompleted: [],        
  sprintsUncompleted: [],      
  tasksByDay: []               
});

const chartData = computed(() => {
  if (selectedAnalytics.value === "Tasks Completed by User") {
    const labels = completedByUser.value.map(u => u.full_name);
    const counts = completedByUser.value.map(u => (u.completed_tasks || []).length);
    tooltipPayload.value.completedByUser = completedByUser.value.map(u => u.completed_tasks || []);
    return {
      labels,
      datasets: [
        { label: "Completed Tasks", backgroundColor: "#42A5F5", data: counts }
      ]
    };
  }

  if (selectedAnalytics.value === "Tasks in Sprint (Completed / In Progress)") {
    const labels = sprintStatus.value.map(s => s.name);
    const completed   = sprintStatus.value.map(s => (s.completed_tasks   || []).length);
    const uncompleted = sprintStatus.value.map(s => (s.uncompleted_tasks || []).length);
    tooltipPayload.value.sprintsCompleted   = sprintStatus.value.map(s => s.completed_tasks   || []);
    tooltipPayload.value.sprintsUncompleted = sprintStatus.value.map(s => s.uncompleted_tasks || []);
    return {
      labels,
      datasets: [
        { label: "Completed",   backgroundColor: "#66BB6A", data: completed },
        { label: "In Progress", backgroundColor: "#FFA726", data: uncompleted }
      ]
    };
  }

  const labels = progressByDay.value.map(d => d.day); 
  const counts = progressByDay.value.map(d => (d.tasks || []).length);
  tooltipPayload.value.tasksByDay = progressByDay.value.map(d => d.tasks || []);
  return {
    labels,
    datasets: [
      { label: "Tasks Completed", backgroundColor: "#FF6384", data: counts }
    ]
  };
});

const maxY = computed(() => {
  const ds = chartData.value?.datasets || [];
  const all = ds.flatMap(d => d.data || [0]);
  return Math.max(5, ...(all.length ? all : [0]));
});

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: "top",
      labels: { color: "#fff" }
    },
    tooltip: {
      callbacks: {
        title: (items) => {
          const i = items?.[0];
          return i ? chartData.value.labels[i.dataIndex] : "";
        },
        label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y}`,
        afterLabel: (ctx) => {
          const idx = ctx.dataIndex;
          if (selectedAnalytics.value === "Tasks Completed by User") {
            const list = tooltipPayload.value.completedByUser[idx] || [];
            return list.length ? ["", "Tasks:", ...list.map(t => `• ${t}`)] : ["", "Tasks: —"];
          }
          if (selectedAnalytics.value === "Tasks in Sprint (Completed / In Progress)") {
            const isCompleted = ctx.datasetIndex === 0;
            const list = isCompleted
              ? (tooltipPayload.value.sprintsCompleted[idx]   || [])
              : (tooltipPayload.value.sprintsUncompleted[idx] || []);
            const title = isCompleted ? "Completed:" : "In progress:";
            return list.length ? ["", title, ...list.map(t => `• ${t}`)] : ["", `${title} —`];
          }
          const list = tooltipPayload.value.tasksByDay[idx] || [];
          return list.length ? ["", "Completed:", ...list.map(t => `• ${t}`)] : ["", "Completed: —"];
        }
      }
    }
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { color: "#aaa" }
    },
    y: {
      beginAtZero: true,
      suggestedMax: maxY.value,
      grid: { color: "#444" },
      ticks: { color: "#aaa" }
    }
  }
}));
</script>



<style scoped>
.analytics-container {
  max-width: 1300px;
  margin: auto;
  padding-top: 20px;
}

.filters-card {
  background-color: #1e1e1e;
  border-radius: 8px;
}

.chart-card {
  background-color: #1e1e1e;
  height: 660px;
  border-radius: 8px;
  overflow: hidden;
}

.chart-card h4 {
  color: #fff;
}

.chart-card .v-container {
  height: 100%;
}

.chart-card .v-row {
  height: 100%;
}

.chart-card .v-col {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>