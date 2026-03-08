<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { toast } from "vue-sonner";
import AuthForm from "@/components/auth/AuthForm.vue";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const router = useRouter();
const route = useRoute();
const isRegister = ref(false);

onMounted(() => {
  if (route.query.expired === "true") {
    toast.info("Session Expired", {
      description: "Please log in again to continue.",
    });
  }
});

function onAuthSuccess() {
  router.push("/dashboard");
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-background px-4">
    <Card class="w-full max-w-md">
      <CardHeader class="text-center">
        <CardTitle class="text-2xl">Leave Management</CardTitle>
        <CardDescription>
          {{ isRegister ? "Create an account" : "Welcome back" }}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <AuthForm
          :key="isRegister ? 'register' : 'login'"
          :mode="isRegister ? 'register' : 'login'"
          @success="onAuthSuccess"
        />

        <p class="mt-4 text-center text-sm text-muted-foreground">
          {{
            isRegister ? "Already have an account?" : "Don't have an account?"
          }}
          <Button
            variant="ghost"
            class="p-0 h-auto cursor-pointer"
            @click="isRegister = !isRegister"
          >
            {{ isRegister ? "Login" : "Register" }}
          </Button>
        </p>
      </CardContent>
    </Card>
  </div>
</template>
