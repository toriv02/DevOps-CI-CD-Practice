<script setup>
import { ref, onBeforeMount } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import Cookies from 'js-cookie';

const contents = ref([])
const types = ref([])
const contentToAdd = ref({
  name: '',
  type_id: null
})
const contentToEdit = ref({
  id: null,
  name: '',
  type_id: null
})

const router = useRouter();

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
})

onBeforeMount(async () => {
  await fetchContents()
  await fetchTypes()
})

async function fetchTypes() {
  try {
    const r = await axios.get("/api/types/");
    types.value = r.data;
  } catch (error) {
    console.error('Ошибка загрузки типов:', error);
  }
}

async function fetchContents() {
  try {
    const r = await axios.get("/api/contents/");
    contents.value = r.data;
  } catch (error) {
    console.error('Ошибка загрузки контента:', error);
  }
}

async function onContentAdd() {
  try {
    await axios.post("/api/contents/", {
      name: contentToAdd.value.name,
      type_id: contentToAdd.value.type_id
    });
    await fetchContents();
    contentToAdd.value = { name: '', type_id: null };
  } catch (error) {
    console.error('Ошибка добавления контента:', error);
  }
}

async function onRemoveClick(content) {
  try {
    await axios.delete(`/api/contents/${content.id}/`);
    await fetchContents();
  } catch (error) {
    console.error('Ошибка удаления контента:', error);
  }
}

async function onContentEditClick(content) {
  contentToEdit.value = { 
    id: content.id,
    name: content.name,
    type_id: content.type ? content.type.id : null
  };
}

async function onUpdateContent() {
  try {
    await axios.put(`/api/contents/${contentToEdit.value.id}/`, {
      name: contentToEdit.value.name,
      type_id: contentToEdit.value.type_id
    });
    await fetchContents();
    contentToEdit.value = { id: null, name: '', type_id: null };
  } catch (error) {
    console.error('Ошибка обновления контента:', error);
  }
}

</script>

<template>
  <form @submit.prevent.stop="onContentAdd">
    <div class="row">
      <div class="col">
        <div class="form-floating">
          <input
            type="text"
            class="form-control"
            v-model="contentToAdd.name"
            placeholder="Название контента"
            required
          />
          <label for="floatingInput">Название контента</label>
        </div>
      </div>
      <div class="col">
        <div class="form-floating">
          <select class="form-select" v-model="contentToAdd.type_id" required>
            <option value="" disabled selected>Выберите тип</option>
            <option v-for="type in types" :key="type.id" :value="type.id">
              {{ type.name }}
            </option>
          </select>
          <label for="floatingSelect">Тип контента</label>
        </div>
      </div>
      <div class="col-auto">
        <button class="btn btn-primary">
          Добавить контент
        </button>
      </div>
    </div>
  </form>

  <div class="check-content-container">
    <div v-if="!contents.length">
      <p class="text-white">Нет контента</p>
    </div>
    <div v-else>
      <div v-for="item in contents" :key="item.id" class="content-item">
        <div>
          <div><strong>{{ item.name }}</strong></div>
          <div class="text-muted">Тип: {{ item.type ? item.type.name : 'Без типа' }}</div>
        </div>
        <div class="content-actions">
          <button
            class="btn btn-success"
            @click="onContentEditClick(item)"
            data-bs-toggle="modal"
            data-bs-target="#editContentModal"
          >
            <i class="bi bi-pen-fill"></i>
          </button>
          <button class="btn btn-danger" @click="onRemoveClick(item)">
            <i class="bi bi-x"></i>
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Модальное окно для редактирования контента -->
  <div class="modal fade" id="editContentModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="exampleModalLabel">
            Редактировать контент
          </h1>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body">
          <div class="row">
            <div class="col">
              <div class="form-floating">
                <input
                  type="text"
                  class="form-control"
                  v-model="contentToEdit.name"
                  placeholder="Название контента"
                />
                <label for="floatingInput">Название контента</label>
              </div>
            </div>
            <div class="col">
              <div class="form-floating">
                <select class="form-select" v-model="contentToEdit.type_id">
                  <option value="" disabled>Выберите тип</option>
                  <option v-for="type in types" :key="type.id" :value="type.id">
                    {{ type.name }}
                  </option>
                </select>
                <label for="floatingSelect">Тип контента</label>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-secondary"
            data-bs-dismiss="modal"
          >
            Закрыть
          </button>
          <button
            data-bs-dismiss="modal"
            type="button"
            class="btn btn-primary"
            @click="onUpdateContent"
          >
            Сохранить
          </button>
        </div>
      </div>
    </div>
  </div>

</template>

<style scoped>
.content-item {
  padding: 0.5rem;
  margin: 0.5rem 0;
  border: 1px solid silver;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #fff;
  background-color: #495057;
}

.content-actions {
  flex: none;
  display: flex;
  gap: 0.5rem;
}

.row {
  margin-top: 10px;
}

.row>div {
  margin-bottom: 1rem;
}

.row>div:last-child {
  margin-bottom: 0;
}

.row>div>.form-floating {
  margin-bottom: 1rem;
}

.row>div>.form-floating:last-child {
  margin-bottom: 0;
}

.form-floating label {
  margin-bottom: 0.5rem;
}

.check-content-container {
  max-width: 1000px;
  margin: 20px auto;
  padding: 20px;
  border-radius: 1rem;
  background-color: #343a40;
}

.form-floating {
  position: relative;
}

.form-control, .form-select {
  background-color: #000c18;
  color: #fff;
  border: 1px solid #6c757d;
}

.form-control:focus, .form-select:focus {
  background-color: #495057;
  color: #fff;
  border-color: #86b7fe;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
}

.form-control::placeholder {
  color: #adb5bd;
}

.btn-primary {
  background-color: #0d6efd;
  border-color: #0d6efd;
  height: 58px;
}

.btn-success {
  background-color: #198754;
  border-color: #198754;
}

.btn-danger {
  background-color: #dc3545;
  border-color: #dc3545;
}

.text-muted {
  color: #adb5bd !important;
}
</style>