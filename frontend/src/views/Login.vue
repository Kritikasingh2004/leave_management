<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "@/lib/api";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const router = useRouter();

// Toggle between Employee / Employer
const role = ref<"employee" | "employer">("employee");

// Toggle between Login / Register
const isRegister = ref(false);

const name = ref("");
const email = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);

async function handleSubmit() {
  error.value = "";
  loading.value = true;

  try {
    if (isRegister.value) {
      // Register
      const { data } = await api.post("/auth/register", {
        name: name.value,
        email: email.value,
        password: password.value,
        role: role.value,
      });
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      router.push("/dashboard");
    } else {
      // Login
      const { data } = await api.post("/auth/login", {
        email: email.value,
        password: password.value,
      });
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      router.push("/dashboard");
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || "Something went wrong";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-background px-4">
    <Card class="w-full max-w-md">
      <CardHeader class="text-center">
        <CardTitle class="text-2xl">Leave Management System</CardTitle>
        <CardDescription>
          {{ isRegister ? "Create a new account" : "Sign in to your account" }}
        </CardDescription>
      </CardHeader>

      <CardContent>
        <!-- Role Toggle -->
        <div class="flex rounded-lg border mb-6">
          <button
            :class="[
              'flex-1 py-2 text-sm font-medium rounded-l-lg transition-colors',
              role === 'employee'
                ? 'bg-primary text-primary-foreground'
                : 'hover:bg-muted',
            ]"
            @click="role = 'employee'"
          >
            Employee
          </button>
          <button
            :class="[
              'flex-1 py-2 text-sm font-medium rounded-r-lg transition-colors',
              role === 'employer'
                ? 'bg-primary text-primary-foreground'
                : 'hover:bg-muted',
            ]"
            @click="role = 'employer'"
          >
            Employer
          </button>
        </div>

        <form class="space-y-4" @submit.prevent="handleSubmit">
          <!-- Name (register only) -->
          <div v-if="isRegister" class="space-y-2">
            <Label for="name">Full Name</Label>
            <Input id="name" v-model="name" placeholder="John Doe" required />
          </div>

          <div class="space-y-2">
            <Label for="email">Email</Label>
            <Input
              id="email"
              v-model="email"
              type="email"
              placeholder="you@company.com"
              required
            />
          </div>

          <div class="space-y-2">
            <Label for="password">Password</Label>
            <Input
              id="password"
              v-model="password"
              type="password"
              placeholder="••••••••"
              required
            />
          </div>

          <p v-if="error" class="text-sm text-destructive">{{ error }}</p>

          <Button type="submit" class="w-full" :disabled="loading">
            {{ loading ? "Please wait…" : isRegister ? "Register" : "Login" }}
          </Button>
        </form>

        <p class="mt-4 text-center text-sm text-muted-foreground">
          <span v-if="isRegister">
            Already have an account?
            <button class="underline text-primary" @click="isRegister = false">
              Login
            </button>
          </span>
          <span v-else>
            Don't have an account?
            <button class="underline text-primary" @click="isRegister = true">
              Register
            </button>
          </span>
        </p>
      </CardContent>
    </Card>
  </div>
</template>
