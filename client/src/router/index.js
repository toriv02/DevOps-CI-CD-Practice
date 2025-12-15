import { createRouter, createWebHistory } from 'vue-router';
import ContentView from '../views/ContentView.vue';
import TypeView from '../views/TypeView.vue';


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path:"/",
      name: "ContentView",
      component: ContentView
    },
    {
      path:"/type",
      name: "TypeView",
      component: TypeView
    }
  ],
})

export default router
