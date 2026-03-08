<script setup lang="ts">
import "vue-sonner/style.css";
import { Toaster } from "@/components/ui/sonner";
</script>

<template>
  <div>
    <main>
      <router-view />
    </main>
    <Toaster />
  </div>
</template>
