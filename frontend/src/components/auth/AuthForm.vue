<script setup lang="ts">
import { computed, ref } from "vue";
import { toTypedSchema } from "@vee-validate/zod";
import { z } from "zod";
import { Eye, EyeOff, Loader2 } from "lucide-vue-next";
import { toast } from "vue-sonner";
import api from "@/lib/api";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

// ── Props & Emits ───────────────────────────────────────────────────────────
const props = defineProps<{
  mode: "login" | "register";
}>();

const emit = defineEmits<{
  (e: "success"): void;
}>();

// ── Zod schemas ─────────────────────────────────────────────────────────────
const loginSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  password: z.string().min(6, "Password must be at least 6 characters"),
});

const registerSchema = z.object({
  name: z.string().min(1, "Full name is required"),
  email: z.string().email("Please enter a valid email address"),
  password: z.string().min(6, "Password must be at least 6 characters"),
  role: z.enum(["employee", "employer"], {
    required_error: "Role is required",
  }),
});

// ── Reactive state ──────────────────────────────────────────────────────────
const showPassword = ref(false);

const isRegister = computed(() => props.mode === "register");

const activeSchema = computed(() =>
  toTypedSchema(isRegister.value ? registerSchema : loginSchema),
);

// ── Form submission (receives validated values from <Form>) ─────────────────
async function onSubmit(values: Record<string, any>) {
  try {
    if (isRegister.value) {
      const { data } = await api.post("/auth/register", {
        name: values.name,
        email: values.email,
        password: values.password,
        role: values.role,
      });
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      toast.success("Account created successfully!");
    } else {
      const { data } = await api.post("/auth/login", {
        email: values.email,
        password: values.password,
      });
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      toast.success("Logged in successfully!");
    }

    emit("success");
  } catch (err: any) {
    const message = err.response?.data?.detail || "Something went wrong";
    toast.error(isRegister.value ? "Registration failed" : "Login failed", {
      description: message,
    });
  }
}
</script>

<template>
  <!-- Shadcn <Form> wrapper — handles validation & submit -->
  <Form
    v-slot="{ isSubmitting }"
    :validation-schema="activeSchema"
    :initial-values="{ email: '', password: '', role: 'employee' }"
    class="space-y-4"
    @submit="onSubmit"
  >
    <!-- Role toggle (register only) -->
    <FormField v-if="isRegister" v-slot="{ componentField }" name="role">
      <FormItem>
        <FormLabel>Role</FormLabel>
        <FormControl>
          <Tabs
            :model-value="componentField.modelValue as string"
            class="w-full"
            @update:model-value="componentField['onUpdate:modelValue']"
          >
            <TabsList class="grid w-full grid-cols-2">
              <TabsTrigger value="employee">Employee</TabsTrigger>
              <TabsTrigger value="employer">Employer</TabsTrigger>
            </TabsList>
          </Tabs>
        </FormControl>
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Name (register only) -->
    <FormField v-if="isRegister" v-slot="{ componentField }" name="name">
      <FormItem>
        <FormLabel>Full Name</FormLabel>
        <FormControl>
          <Input placeholder="John Doe" v-bind="componentField" />
        </FormControl>
        <FormMessage />
      </FormItem>
    </FormField>

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

    <!-- Password with show / hide toggle -->
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

    <!-- Submit button with loader -->
    <Button type="submit" class="w-full" :disabled="isSubmitting">
      <Loader2 v-if="isSubmitting" class="size-4 mr-2 animate-spin" />
      {{ isSubmitting ? "Please wait…" : isRegister ? "Register" : "Login" }}
    </Button>
  </Form>
</template>
