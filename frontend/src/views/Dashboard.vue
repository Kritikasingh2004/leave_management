<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
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
}

const user = ref<User | null>(null);
const leaves = ref<LeaveRequest[]>([]);

const isEmployee = computed(() => user.value?.role === "employee");
const isEmployer = computed(() => user.value?.role === "employer");

// ── Lifecycle ───────────────────────────────────────────────────────────────
onMounted(() => {
  const stored = localStorage.getItem("user");
  if (!stored) {
    router.push("/");
    return;
  }
  user.value = JSON.parse(stored);
  fetchLeaves();
});

async function fetchLeaves() {
  try {
    const { data } = await api.get("/leaves/all");
    leaves.value = data;
  } catch {
    // silently fail for now
  }
}

// ── Logout ──────────────────────────────────────────────────────────────────
function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  router.push("/");
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
      <!-- ─── EMPLOYEE VIEW ──────────────────────────────────────────── -->
      <Tabs v-if="isEmployee" default-value="my-requests">
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

      <!-- ─── EMPLOYER VIEW ──────────────────────────────────────────── -->
      <Tabs v-if="isEmployer" default-value="all-requests">
        <TabsList>
          <TabsTrigger value="all-requests" class="p-2"
            >All Requests</TabsTrigger
          >
        </TabsList>

        <TabsContent value="all-requests">
          <Card>
            <CardHeader>
              <CardTitle>All Leave Requests</CardTitle>
            </CardHeader>
            <CardContent>
              <LeaveTable
                :leaves="leaves"
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
