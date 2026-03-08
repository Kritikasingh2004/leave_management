<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { useForm } from "vee-validate";
import { toTypedSchema } from "@vee-validate/zod";
import { z } from "zod";
import { Loader2 } from "lucide-vue-next";
import { toast } from "vue-sonner";
import api from "@/lib/api";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
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
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";

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

// ── Leave application Zod schema ────────────────────────────────────────────
const leaveSchema = toTypedSchema(
  z
    .object({
      type: z.enum(["sick", "casual", "annual", "other"], {
        required_error: "Please select a leave type",
      }),
      start_date: z.string().min(1, "Start date is required"),
      end_date: z.string().min(1, "End date is required"),
      reason: z.string().min(1, "Reason is required"),
    })
    .refine((data) => new Date(data.end_date) >= new Date(data.start_date), {
      message: "End date cannot be before start date",
      path: ["end_date"],
    }),
);

const { handleSubmit, resetForm } = useForm({
  validationSchema: leaveSchema,
  initialValues: {
    type: "casual",
    start_date: "",
    end_date: "",
    reason: "",
  },
});

const isSubmitting = ref(false);

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
const applyLeave = handleSubmit(async (values) => {
  isSubmitting.value = true;
  try {
    await api.post("/leaves/apply", {
      type: values.type,
      start_date: values.start_date,
      end_date: values.end_date,
      reason: values.reason,
    });
    toast.success("Leave applied successfully!");
    resetForm();
    await fetchLeaves();
  } catch (err: any) {
    const message = err.response?.data?.detail || "Failed to apply for leave";
    toast.error("Leave application failed", { description: message });
  } finally {
    isSubmitting.value = false;
  }
});

// ── Approve / Reject (Employer) ─────────────────────────────────────────────
async function updateStatus(leaveId: string, status: "approved" | "rejected") {
  try {
    await api.patch(`/leaves/${leaveId}`, { status });
    toast.success(`Leave request ${status}`);
    await fetchLeaves();
  } catch {
    toast.error("Failed to update leave status");
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
            <form class="grid gap-4 sm:grid-cols-2" @submit="applyLeave">
              <FormField v-slot="{ componentField }" name="type">
                <FormItem class="space-y-2">
                  <FormLabel>Leave Type</FormLabel>
                  <Select v-bind="componentField">
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="sick">Sick</SelectItem>
                      <SelectItem value="casual">Casual</SelectItem>
                      <SelectItem value="annual">Annual</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              </FormField>

              <FormField v-slot="{ componentField }" name="start_date">
                <FormItem class="space-y-2">
                  <FormLabel>Start Date</FormLabel>
                  <FormControl>
                    <Input type="date" v-bind="componentField" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              </FormField>

              <FormField v-slot="{ componentField }" name="end_date">
                <FormItem class="space-y-2">
                  <FormLabel>End Date</FormLabel>
                  <FormControl>
                    <Input type="date" v-bind="componentField" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              </FormField>

              <FormField v-slot="{ componentField }" name="reason">
                <FormItem class="space-y-2 sm:col-span-2">
                  <FormLabel>Reason</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Brief reason for leave"
                      v-bind="componentField"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              </FormField>

              <div class="sm:col-span-2">
                <Button type="submit" :disabled="isSubmitting">
                  <Loader2
                    v-if="isSubmitting"
                    class="size-4 mr-2 animate-spin"
                  />
                  {{ isSubmitting ? "Submitting…" : "Submit Request" }}
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
