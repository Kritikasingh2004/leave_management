<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { toast } from "vue-sonner";
import { Loader2 } from "lucide-vue-next";
import api from "@/lib/api";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

import LeaveRequestForm from "@/components/dashboard/LeaveRequestForm.vue";
import LeaveTable from "@/components/dashboard/LeaveTable.vue";

const router = useRouter();

// ── Current user ────────────────────────────────────────────────────────────
interface User {
  id: string;
  name: string;
  email: string;
  role: "employee" | "employer";
}

interface LeaveRequest {
  id: string;
  employee_id: string;
  employee_name: string;
  type: string;
  start_date: string;
  end_date: string;
  reason: string;
  status: "pending" | "approved" | "rejected";
  admin_note?: string;
}

const user = ref<User | null>(null);
const leaves = ref<LeaveRequest[]>([]);
const isLoading = ref(true);

const isEmployee = computed(() => user.value?.role === "employee");
const isEmployer = computed(() => user.value?.role === "employer");

// ── Filtered lists for employer tabs ────────────────────────────────────────
const pendingLeaves = computed(() =>
  leaves.value.filter((l) => l.status === "pending"),
);
const historyLeaves = computed(() =>
  leaves.value.filter((l) => l.status !== "pending"),
);

// ── Lifecycle ───────────────────────────────────────────────────────────────
onMounted(async () => {
  isLoading.value = true;
  // Prefer /auth/me to validate token; fall back to localStorage
  try {
    const { data } = await api.get("/auth/me");
    user.value = data;
    // Keep localStorage in sync
    localStorage.setItem("user", JSON.stringify(data));
  } catch {
    const stored = localStorage.getItem("user");
    if (!stored) {
      router.push("/login");
      return;
    }
    user.value = JSON.parse(stored);
  }

  await fetchLeaves();
  isLoading.value = false;
});

async function fetchLeaves() {
  try {
    const { data } = await api.get("/leaves/all");
    leaves.value = data;
  } catch (err: any) {
    const message =
      err.response?.data?.detail || "Failed to fetch leave requests";
    toast.error("Error", { description: message });
  }
}

// ── Logout ──────────────────────────────────────────────────────────────────
function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  router.push("/login");
}
</script>

<template>
  <div class="min-h-screen bg-background">
    <!-- Navbar -->
    <header class="border-b">
      <div
        class="max-w-6xl mx-auto flex items-center justify-between px-6 py-4"
      >
        <h1 class="text-lg font-semibold">Leave Management</h1>
        <div class="flex items-center gap-4">
          <span class="text-sm text-muted-foreground">
            {{ user?.name }} ({{ user?.role }})
          </span>
          <Button variant="neutral" size="sm" @click="logout">Logout</Button>
        </div>
      </div>
    </header>

    <main class="max-w-6xl mx-auto px-6 py-8 space-y-8">
      <!-- ─── LOADING STATE ───────────────────────────────────────────────── -->
      <div
        v-if="isLoading"
        class="flex flex-col items-center justify-center py-24 gap-4"
      >
        <Loader2 class="size-8 animate-spin text-muted-foreground" />
        <p class="text-sm text-muted-foreground">Loading dashboard…</p>
      </div>

      <!-- ─── EMPLOYEE VIEW ───────────────────────────────────────────────── -->
      <Tabs v-if="!isLoading && isEmployee" default-value="my-requests">
        <TabsList>
          <TabsTrigger value="my-requests" class="p-2">My Requests</TabsTrigger>
          <TabsTrigger value="new-request" class="p-2">New Request</TabsTrigger>
        </TabsList>

        <TabsContent value="my-requests">
          <Card>
            <CardHeader>
              <CardTitle>My Leave Requests</CardTitle>
            </CardHeader>
            <CardContent>
              <LeaveTable
                :leaves="leaves"
                :is-admin="false"
                @updated="fetchLeaves"
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="new-request">
          <Card>
            <CardHeader>
              <CardTitle>Request Leave</CardTitle>
            </CardHeader>
            <CardContent>
              <LeaveRequestForm @submitted="fetchLeaves" />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <!-- ─── EMPLOYER VIEW ───────────────────────────────────────────────── -->
      <Tabs v-if="!isLoading && isEmployer" default-value="pending">
        <TabsList>
          <TabsTrigger value="pending" class="p-2"
            >Pending Approvals</TabsTrigger
          >
          <TabsTrigger value="history" class="p-2">Leave History</TabsTrigger>
        </TabsList>

        <TabsContent value="pending">
          <Card>
            <CardHeader>
              <CardTitle>Pending Approvals</CardTitle>
            </CardHeader>
            <CardContent>
              <LeaveTable
                :leaves="pendingLeaves"
                :is-admin="true"
                @updated="fetchLeaves"
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history">
          <Card>
            <CardHeader>
              <CardTitle>Leave History</CardTitle>
            </CardHeader>
            <CardContent>
              <LeaveTable
                :leaves="historyLeaves"
                :is-admin="true"
                @updated="fetchLeaves"
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </main>
  </div>
</template>
