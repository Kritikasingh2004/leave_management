<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useForm } from "vee-validate";
import { toTypedSchema } from "@vee-validate/zod";
import { z } from "zod";
import { Eye, EyeOff } from "lucide-vue-next";
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
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";

const router = useRouter();

// Zod schema
const loginSchema = toTypedSchema(
  z.object({
    email: z.string().email("Please enter a valid email address"),
    password: z.string().min(6, "Password must be at least 6 characters"),
  }),
);

const { handleSubmit } = useForm({
  validationSchema: loginSchema,
});

// Toggle between Employee / Employer
const role = ref<"employee" | "employer">("employee");

// Toggle between Login / Register
const isRegister = ref(false);

// Show / hide password
const showPassword = ref(false);

const name = ref("");
const serverError = ref("");
const loading = ref(false);

const onSubmit = handleSubmit(async (values) => {
  serverError.value = "";
  loading.value = true;

  try {
    if (isRegister.value) {
      const { data } = await api.post("/auth/register", {
        name: name.value,
        email: values.email,
        password: values.password,
        role: role.value,
      });
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      router.push("/dashboard");
    } else {
      const { data } = await api.post("/auth/login", {
        email: values.email,
        password: values.password,
      });
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      router.push("/dashboard");
    }
  } catch (err: any) {
    serverError.value = err.response?.data?.detail || "Something went wrong";
  } finally {
    loading.value = false;
  }
});
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
            type="button"
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
            type="button"
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

        <form class="space-y-4" @submit="onSubmit">
          <!-- Name (register only) -->
          <div v-if="isRegister" class="space-y-2">
            <label for="name" class="text-sm font-medium leading-none">
              Full Name
            </label>
            <Input id="name" v-model="name" placeholder="John Doe" required />
          </div>

          <!-- Email -->
          <FormField v-slot="{ componentField }" name="email">
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input
                  type="email"
                  placeholder="you@company.com"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <!-- Password with show/hide toggle -->
          <FormField v-slot="{ componentField }" name="password">
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <div class="relative">
                  <Input
                    :type="showPassword ? 'text' : 'password'"
                    placeholder="••••••••"
                    v-bind="componentField"
                  />
                  <button
                    type="button"
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                    @click="showPassword = !showPassword"
                  >
                    <EyeOff v-if="showPassword" class="size-4" />
                    <Eye v-else class="size-4" />
                  </button>
                </div>
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <p v-if="serverError" class="text-sm text-destructive">
            {{ serverError }}
          </p>

          <Button type="submit" class="w-full" :disabled="loading">
            {{ loading ? "Please wait…" : isRegister ? "Register" : "Login" }}
          </Button>
        </form>

        <p class="mt-4 text-center text-sm text-muted-foreground">
          <span v-if="isRegister">
            Already have an account?
            <button
              type="button"
              class="underline text-primary"
              @click="isRegister = false"
            >
              Login
            </button>
          </span>
          <span v-else>
            Don't have an account?
            <button
              type="button"
              class="underline text-primary"
              @click="isRegister = true"
            >
              Register
            </button>
          </span>
        </p>
      </CardContent>
    </Card>
  </div>
</template>
