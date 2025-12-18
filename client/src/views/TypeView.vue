<script setup>
import { ref, onBeforeMount } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import Cookies from 'js-cookie';


const types = ref([])
const typeToAdd = ref({})
const typeToEdit = ref({})

const router = useRouter();

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
})

onBeforeMount(async () => {
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

async function onTypeAdd() {
  await axios.post("/api/types/", {
    ...typeToAdd.value,
  });
  await fetchTypes();
  typeToAdd.value = {};
}

async function onRemoveClick(type) {
  await axios.delete(`/api/types/${type.id}/`);
  await fetchTypes();
}

async function onTypeEditClick(type) {
  typeToEdit.value = { ...type };
}

async function onUpdateType() {
  await axios.put(`/api/types/${typeToEdit.value.id}/`, {
    ...typeToEdit.value,
  });
  await fetchTypes();
}

</script>

<template>
  <form @submit.prevent.stop="onTypeAdd">
    <div class="row">
      <div class="col">
        <div class="form-floating">
          <input
            type="text"
            class="form-control"
            v-model="typeToAdd.name"
            required
          />
          <label for="floatingInput">Название типа!</label>
        </div>
      </div>
      <div class="col-auto">
        <button class="btn btn-primary">
          Добавить тип
        </button>
      </div>
    </div>
  </form>

  <div class="check-type-container">
    <div v-if="!types.length">
      <p class="text-white">Нет типов</p>
    </div>
    <div v-else>
      <div v-for="item in types" :key="item.id" class="type-item">
        <div>{{ item.name }}</div>
        <div class="type-actions">
          <button
            class="btn btn-success"
            @click="onTypeEditClick(item)"
            data-bs-toggle="modal"
            data-bs-target="#editTypeModal"
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

  <!-- Модальное окно для редактирования типа -->
  <div class="modal fade" id="editTypeModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="exampleModalLabel">
            Редактировать тип
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
                  v-model="typeToEdit.name"
                />
                <label for="floatingInput">Наименование типа</label>
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
            @click="onUpdateType"
          >
            Сохранить
          </button>
        </div>
      </div>
    </div>
  </div>

</template>

<style scoped>
.type-item {
  padding: 0.5rem;
  margin: 0.5rem 0;
  border: 1px solid silver;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #fff;
}

.type-actions {
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

.check-type-container {
  max-width: 1000px;
  margin: 20px auto;
  padding: 20px;
  border-radius: 1rem;
  background-color: #343a40;
}

.type-card {
  border: 1px solid #eee;
  margin-bottom: 20px;
  padding: 15px;
  border-radius: 5px;
  cursor: pointer;
  text-decoration: none;
  color: #333;
  display: block;
  transition: background-color 0.3s ease;
  background-color: #495057;
}

.button-container {
  display: flex;
  gap: 1rem;
}
</style>