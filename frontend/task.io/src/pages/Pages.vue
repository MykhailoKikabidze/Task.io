<route lang="yaml">
  meta:
    layout: navigation
  </route>
  
  <template>
    <v-container>
      <v-row class="mb-4 justify-center">
        <v-col cols="12">
          <h2 class="text-h5 font-weight-bold text-center">Pages</h2>
          <p class="text-subtitle-1 text-medium-emphasis text-center">
            Create, edit, and manage pages
          </p>
        </v-col>
      </v-row>
  
      <v-row class="justify-center">
        <v-col cols="12" md="3">
          <v-card class="pa-3 mb-4" elevation="20">
            <v-card-title class="text-h6">Pages</v-card-title>
            <v-divider class="mb-2" />
  
            <div class="pages-list">
              <v-list dense>
                <v-list-item
                  v-for="(page, index) in pages"
                  :key="index"
                  class="mb-2"
                  @click="selectPage(index)"
                >
                  <v-card
                    class="pa-2 w-100 d-flex align-center page-item"
                    :class="{ 'selected-item': index === selectedPageIndex }"
                    color="grey-darken-3"
                  >
                    <div
                      class="text-subtitle-2 font-weight-medium"
                      :class="{ 'selected-text': index === selectedPageIndex }"
                    >
                      {{ page.title }}
                    </div>
                  </v-card>
                </v-list-item>
              </v-list>
            </div>
  
            <v-btn
              color="blue"
              block
              class="mt-4 fixed-btn"
              @click="showDialog = true"
            >
              ADD PAGE
            </v-btn>
          </v-card>
        </v-col>
  
        <v-col cols="12" md="7">
          <v-card class="pa-4" elevation="20">
            <v-textarea
              label="Page Content"
              rows="15"
              v-model="pageContent"
              :disabled="!isPageSelected || isSaved"
            />
  
            <v-row dense class="mt-4">
              <v-col cols="6">
                <v-btn
                  color="blue"
                  block
                  :disabled="!isPageSelected"
                  @click="savePage"
                >
                  SAVE
                </v-btn>
              </v-col>
              <v-col cols="6">
                <v-btn
                  color="red"
                  block
                  :disabled="!isPageSelected"
                  @click="deletePage"
                >
                  DELETE
                </v-btn>
              </v-col>
            </v-row>
          </v-card>
        </v-col>
      </v-row>
  
      <v-dialog v-model="showDialog" width="500">
        <v-card>
          <v-card-title>Add a new page</v-card-title>
          <v-card-text>
            <v-text-field
              v-model="newPage.title"
              label="Page title *"
              prepend-inner-icon="mdi-format-title"
              dense
              outlined
              required
            />
            <v-textarea
              v-model="newPage.content"
              label="Page content"
              rows="5"
              auto-grow
              prepend-inner-icon="mdi-text-box-outline"
              dense
              outlined
            />
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn text @click="closeDialog">Cancel</v-btn>
            <v-btn
              color="primary"
              :disabled="!newPage.title.trim()"
              @click="createPage"
            >
              Create
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-container>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue';
  
  const pages = ref([
    { title: 'Page 1', content: 'This is the content of Page 1' },
    { title: 'Page 2', content: 'This is the content of Page 2' },
    { title: 'Page 3', content: 'This is the content of Page 3' }
  ]);
  
  const selectedPageIndex = ref(null);
  const pageContent = ref('');
  const isSaved = ref(true);
  
  const isPageSelected = computed(() => selectedPageIndex.value !== null);
  
  function selectPage(index) {
    selectedPageIndex.value = index;
    pageContent.value = pages.value[index].content;
    isSaved.value = false;
  }
  
  function savePage() {
    if (isPageSelected.value) {
      pages.value[selectedPageIndex.value].content = pageContent.value;
      isSaved.value = true;
    }
  }
  
  function deletePage() {
    if (!isPageSelected.value) return;
    if (confirm('Delete this page?')) {
      pages.value.splice(selectedPageIndex.value, 1);
      selectedPageIndex.value = null;
      pageContent.value = '';
      isSaved.value = true;
    }
  }
  
  const showDialog = ref(false);
  const newPage = ref({ title: '', content: '' });
  
  function closeDialog() {
    newPage.value = { title: '', content: '' };
    showDialog.value = false;
  }
  function createPage() {
    pages.value.push({
      title: newPage.value.title.trim(),
      content: newPage.value.content
    });
    closeDialog();
  }
  </script>
  
  <style scoped>
  .v-card-title {
    padding-bottom: 0;
  }
  
  .v-container {
    max-width: 1600px;
  }
  
  .v-row {
    justify-content: center;
  }
  
  .pages-list {
    max-height: 400px;
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: #1e88e5 #333;
  }
  .pages-list::-webkit-scrollbar {
    width: 8px;
  }
  .pages-list::-webkit-scrollbar-track {
    background: #333;
    border-radius: 4px;
  }
  .pages-list::-webkit-scrollbar-thumb {
    background: #1e88e5;
    border-radius: 4px;
  }
  
  .page-item {
    cursor: pointer;
    transition: background-color 0.3s, color 0.3s, box-shadow 0.3s;
  }
  .page-item.selected-item {
    border-left: 4px solid #1e88e5;
  }
  .selected-text {
    color: #1e88e5;
    font-weight: 600;
  }
  
  .fixed-btn {
    position: sticky;
    bottom: 16px;
  }
  </style>
  