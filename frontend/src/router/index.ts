import { createRouter, createWebHistory } from "vue-router";
import Login from "@/views/Login.vue";
import Dashboard from "@/views/Dashboard.vue";

const routes = [
  {
    path: "/",
    name: "Login",
    component: Login,
  },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: Dashboard,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation guard — protect routes that require authentication
router.beforeEach((to, _from, next) => {
  if (to.meta.requiresAuth && !localStorage.getItem("token")) {
    next({ name: "Login" });
  } else {
    next();
  }
});

export default router;
