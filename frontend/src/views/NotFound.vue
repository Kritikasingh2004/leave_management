<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";
import { FileQuestion } from "lucide-vue-next";
import { Button } from "@/components/ui/button";

const router = useRouter();
const isAuthenticated = computed(() => !!localStorage.getItem("token"));

function goBack() {
  router.push(isAuthenticated.value ? { name: "Dashboard" } : { name: "Login" });
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-background px-4">
    <div class="text-center space-y-6">
      <div class="flex justify-center">
        <FileQuestion class="h-20 w-20 text-muted-foreground" :stroke-width="1.25" />
      </div>

      <h1 class="text-7xl font-extrabold tracking-tight text-foreground">404</h1>

      <p class="text-lg text-muted-foreground max-w-md mx-auto">
        The page you are looking for doesn't exist.
      </p>

      <Button size="lg" @click="goBack">
        {{ isAuthenticated ? "Back to Dashboard" : "Go to Login" }}
      </Button>
    </div>
  </div>
</template>
