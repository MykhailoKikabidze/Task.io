<route lang="yaml">
    meta:
      layout: navigation
  </route>
  
  <template>
    <v-container>
      <v-row class="mb-4 justify-space-between">
        <v-col cols="6">
          <v-select
            v-model="selectedProject"
            :items="projectOptions"
            label="Select Project"
          ></v-select>
        </v-col>
  
        <v-col cols="6">
          <v-select
            v-model="sortOption"
            :items="sortOptions"
            label="Sort By"
          ></v-select>
        </v-col>
      </v-row>
  
      <v-row class="justify-center">
        <v-col cols="12" md="8">
          <v-card class="pa-3" elevation="20">
            <v-card-title class="text-h6">Notification Content</v-card-title>
            <v-divider class="mb-2"></v-divider>
            <div class="notification-content">
              <p v-if="selectedNotification">
                {{ selectedNotification.content }}
              </p>
              <p v-else class="text-muted">Select a notification to view details</p>
            </div>
          </v-card>
        </v-col>
  
        <v-col cols="12" md="4">
          <v-card class="pa-3" elevation="20">
            <v-card-title class="text-h6">Notifications</v-card-title>
            <v-divider class="mb-2"></v-divider>
  
            <div class="notification-list-container">
              <v-list dense>
                <v-list-item
                  v-for="(notification, index) in filteredNotifications"
                  :key="index"
                  class="mb-2"
                  :class="{'selected-item': index === selectedNotificationIndex}"
                  @click="selectNotification(index)"
                >
                  <v-card class="pa-2 w-100 d-flex align-center justify-space-between" color="grey-darken-3">
                    <div>
                      <div
                        class="text-subtitle-2 font-weight-medium"
                        :class="{ 'selected-text': index === selectedNotificationIndex }"
                      >
                        {{ notification.title }}
                      </div>
                      <div class="text-caption text-medium-emphasis">
                        {{ notification.date }} 
                        <span v-if="selectedProject === 'All'" class="project-label">
                          — {{ notification.project }}
                        </span>
                      </div>
                    </div>
                    <v-icon icon="mdi-arrow-right-circle" class="text-blue" />
                  </v-card>
                </v-list-item>
              </v-list>
            </div>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </template>
  
  <script setup>
  import { ref, computed } from "vue";
  
  const projectOptions = ["All", "Project Alpha", "Project Beta", "Project Gamma"];
  const sortOptions = ["Date", "Title"];
  
  const selectedProject = ref("All");
  const sortOption = ref("Date");
  const selectedNotificationIndex = ref(null);
  
  const notifications = ref([
    { title: "New Task Created", date: "2025-05-10", project: "Project Alpha", content: "A new task has been created in Project Alpha." },
    { title: "Task Updated", date: "2025-05-09", project: "Project Beta", content: "A task has been updated in Project Beta." },
    { title: "Bug Reported", date: "2025-05-08", project: "Project Gamma", content: "A bug has been reported in Project Gamma." },
    { title: "Bug Reported", date: "2025-05-08", project: "Project Alpha", content: "A bug has been reported in Project Alpha." },
    { title: "Bug Reported", date: "2025-05-08", project: "Project Beta", content: "A bug has been reported in Project Beta." },
    { title: "Bug Reported", date: "2025-05-08", project: "Project Beta", content: "A bug has been reported in Project Beta." },
    { title: "Bug Reported", date: "2025-05-08", project: "Project Beta", content: "A bug has been reported in Project Beta." },
    { title: "Bug Reported", date: "2025-05-08", project: "Project Beta", content: "A bug has been reported in Project Beta." },
    { title: "Bug Reported", date: "2025-05-08", project: "Project Beta", content: "A bug has been reported in Project Beta." },
    { title: "Bug Reported", date: "2025-05-08", project: "Project Beta", content: "A bug has been reported in Project Beta." },
    { title: "Bug Reported", date: "2025-05-08", project: "Project Beta", content: "A bug has been reported in Project Beta." },
    { title: "Bug Reported", date: "2025-05-08", project: "Project Beta", content: "A bug has been reported in Project Beta." },
  ]);
  
  const filteredNotifications = computed(() => {
    let filtered = notifications.value;
  
    if (selectedProject.value !== "All") {
      filtered = filtered.filter((n) => n.project === selectedProject.value);
    }
  
    if (sortOption.value === "Date") {
      filtered = filtered.sort((a, b) => new Date(b.date) - new Date(a.date));
    } else {
      filtered = filtered.sort((a, b) => a.title.localeCompare(b.title));
    }
  
    return filtered;
  });
  
  const selectedNotification = computed(() => {
    return selectedNotificationIndex.value !== null
      ? filteredNotifications.value[selectedNotificationIndex.value]
      : null;
  });
  
  const selectNotification = (index) => {
    selectedNotificationIndex.value = index;
  };
  </script>
  
  <style scoped>
  .notification-list-container {
    max-height: 460px;
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: #1e88e5 #333333;
  }
  
  .notification-list-container::-webkit-scrollbar {
    width: 8px;
  }
  
  .notification-list-container::-webkit-scrollbar-track {
    background-color: #333333;
    border-radius: 4px;
  }
  
  .notification-list-container::-webkit-scrollbar-thumb {
    background-color: #1e88e5;
    border-radius: 4px;
  }
  
  .selected-item {
    border-left: 4px solid #1e88e5;
  }
  
  .selected-text {
    color: #1e88e5;
    font-weight: bold;
  }
  
  .project-label {
    color: #bbb;
    font-style: italic;
  }
  </style>
  