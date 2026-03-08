<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import api from "@/lib/api";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

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

// ── Leave form state ────────────────────────────────────────────────────────
const leaveType = ref("casual");
const startDate = ref("");
const endDate = ref("");
const reason = ref("");
const formError = ref("");
const formLoading = ref(false);

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

// ── Apply for leave (Employee) ──────────────────────────────────────────────
async function applyLeave() {
  formError.value = "";
  formLoading.value = true;
  try {
    await api.post("/leaves/apply", {
      type: leaveType.value,
      start_date: startDate.value,
      end_date: endDate.value,
      reason: reason.value,
    });
    // Reset form
    leaveType.value = "casual";
    startDate.value = "";
    endDate.value = "";
    reason.value = "";
    await fetchLeaves();
  } catch (err: any) {
    formError.value = err.response?.data?.detail || "Failed to apply";
  } finally {
    formLoading.value = false;
  }
}

// ── Approve / Reject (Employer) ─────────────────────────────────────────────
async function updateStatus(leaveId: string, status: "approved" | "rejected") {
  try {
    await api.patch(`/leaves/${leaveId}`, { status });
    await fetchLeaves();
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

// ── Badge variant helper ────────────────────────────────────────────────────
function badgeVariant(
  status: string,
): "default" | "secondary" | "destructive" | "outline" {
  switch (status) {
    case "approved":
      return "default";
    case "rejected":
      return "destructive";
    default:
      return "secondary";
  }
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
          <Button variant="outline" size="sm" @click="logout">Logout</Button>
        </div>
      </div>
    </header>

    <main class="max-w-6xl mx-auto px-6 py-8 space-y-8">
      <!-- ─── EMPLOYEE VIEW ──────────────────────────────────────────── -->
      <template v-if="isEmployee">
        <!-- Request Leave Form -->
        <Card>
          <CardHeader>
            <CardTitle>Request Leave</CardTitle>
          </CardHeader>
          <CardContent>
            <form
              class="grid gap-4 sm:grid-cols-2"
              @submit.prevent="applyLeave"
            >
              <div class="space-y-2">
                <Label>Leave Type</Label>
                <Select v-model="leaveType">
                  <SelectTrigger>
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="sick">Sick</SelectItem>
                    <SelectItem value="casual">Casual</SelectItem>
                    <SelectItem value="annual">Annual</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div class="space-y-2">
                <Label for="start">Start Date</Label>
                <Input id="start" v-model="startDate" type="date" required />
              </div>
              <div class="space-y-2">
                <Label for="end">End Date</Label>
                <Input id="end" v-model="endDate" type="date" required />
              </div>
              <div class="space-y-2 sm:col-span-2">
                <Label for="reason">Reason</Label>
                <Input
                  id="reason"
                  v-model="reason"
                  placeholder="Brief reason for leave"
                />
              </div>
              <div class="sm:col-span-2">
                <p v-if="formError" class="text-sm text-destructive mb-2">
                  {{ formError }}
                </p>
                <Button type="submit" :disabled="formLoading">
                  {{ formLoading ? "Submitting…" : "Submit Request" }}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        <!-- My Leaves Table -->
        <Card>
          <CardHeader>
            <CardTitle>My Leave Requests</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Type</TableHead>
                  <TableHead>From</TableHead>
                  <TableHead>To</TableHead>
                  <TableHead>Reason</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow v-for="leave in leaves" :key="leave.id">
                  <TableCell class="capitalize">{{ leave.type }}</TableCell>
                  <TableCell>{{ leave.start_date }}</TableCell>
                  <TableCell>{{ leave.end_date }}</TableCell>
                  <TableCell>{{ leave.reason || "—" }}</TableCell>
                  <TableCell>
                    <Badge
                      :variant="badgeVariant(leave.status)"
                      class="capitalize"
                    >
                      {{ leave.status }}
                    </Badge>
                  </TableCell>
                </TableRow>
                <TableRow v-if="leaves.length === 0">
                  <TableCell
                    colspan="5"
                    class="text-center text-muted-foreground"
                  >
                    No leave requests yet.
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </template>

      <!-- ─── EMPLOYER VIEW ──────────────────────────────────────────── -->
      <template v-if="isEmployer">
        <Card>
          <CardHeader>
            <CardTitle>All Leave Requests</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Employee</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>From</TableHead>
                  <TableHead>To</TableHead>
                  <TableHead>Reason</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead class="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow v-for="leave in leaves" :key="leave.id">
                  <TableCell>{{ leave.employee_name }}</TableCell>
                  <TableCell class="capitalize">{{ leave.type }}</TableCell>
                  <TableCell>{{ leave.start_date }}</TableCell>
                  <TableCell>{{ leave.end_date }}</TableCell>
                  <TableCell>{{ leave.reason || "—" }}</TableCell>
                  <TableCell>
                    <Badge
                      :variant="badgeVariant(leave.status)"
                      class="capitalize"
                    >
                      {{ leave.status }}
                    </Badge>
                  </TableCell>
                  <TableCell class="text-right space-x-2">
                    <template v-if="leave.status === 'pending'">
                      <Button
                        size="sm"
                        variant="default"
                        @click="updateStatus(leave.id, 'approved')"
                      >
                        Approve
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        @click="updateStatus(leave.id, 'rejected')"
                      >
                        Reject
                      </Button>
                    </template>
                    <span v-else class="text-sm text-muted-foreground">—</span>
                  </TableCell>
                </TableRow>
                <TableRow v-if="leaves.length === 0">
                  <TableCell
                    colspan="7"
                    class="text-center text-muted-foreground"
                  >
                    No leave requests found.
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </template>
    </main>
  </div>
</template>
