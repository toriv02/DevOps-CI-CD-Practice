<script setup>
import { onBeforeMount } from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie';


import {useRouter, useRoute} from "vue-router";
import 'bootstrap/dist/js/bootstrap.bundle.min'




const router = useRouter();
const route = useRoute();

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
})

const isActive = (routePath) => {
  return route.path === routePath;
};

</script>
<template>
  
  <div class="container">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container-fluid">
        <a class="navbar-brand" href="/"> Пример для ветки dev</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
                aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav mb-2 mb-lg-0">
            <li class="nav-item" :class="{ 'active': isActive('/') }">
              <router-link class="nav-link" to="/">Контент</router-link>
            </li>
            <li class="nav-item" :class="{ 'active': isActive('/type') }">
              <router-link class="nav-link" to="/type">Тип контента</router-link>
            </li>
            <li class="nav-item" :class="{ 'active': isActive('/') }">
              <router-link class="nav-link" to="/">Тестовая кнопка</router-link>
            </li>
          </ul>


          
        </div>
      </div>
    </nav>
  </div>

  


  
  <div class="container">
    <router-view/>
  </div>

</template>



