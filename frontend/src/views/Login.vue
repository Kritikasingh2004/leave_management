<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
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
const isRegister = ref(false);

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
            variant="link"
            class="p-0 h-auto"
            @click="isRegister = !isRegister"
          >
            {{ isRegister ? "Login" : "Register" }}
          </Button>
        </p>
      </CardContent>
    </Card>
  </div>
</template>
