<script setup lang="ts">
import { toast } from "vue-sonner";
import api from "@/lib/api";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

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

const props = defineProps<{
  leaves: LeaveRequest[];
  isAdmin: boolean;
}>();

const emit = defineEmits<{
  (e: "updated"): void;
}>();

// ── Badge colour helper ─────────────────────────────────────────────────────
function badgeClass(status: string): string {
  switch (status) {
    case "approved":
      return "bg-green-100 text-green-800 hover:bg-green-100 dark:bg-green-900 dark:text-green-300";
    case "rejected":
      return "bg-red-100 text-red-800 hover:bg-red-100 dark:bg-red-900 dark:text-red-300";
    default:
      return "bg-yellow-100 text-yellow-800 hover:bg-yellow-100 dark:bg-yellow-900 dark:text-yellow-300";
  }
}

// ── Admin actions ───────────────────────────────────────────────────────────
async function updateStatus(leaveId: string, status: "approved" | "rejected") {
  try {
    await api.patch(`/leaves/${leaveId}`, { status });
    toast.success(`Leave request ${status}`);
    emit("updated");
  } catch {
    toast.error("Failed to update leave status");
  }
}
</script>

<template>
  <Table>
    <TableHeader>
      <TableRow>
        <TableHead v-if="isAdmin">Employee</TableHead>
        <TableHead>Type</TableHead>
        <TableHead>From</TableHead>
        <TableHead>To</TableHead>
        <TableHead>Reason</TableHead>
        <TableHead>Status</TableHead>
        <TableHead v-if="isAdmin" class="text-right">Actions</TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      <TableRow v-for="leave in props.leaves" :key="leave.id">
        <TableCell v-if="isAdmin">{{ leave.employee_name }}</TableCell>
        <TableCell class="capitalize">{{ leave.type }}</TableCell>
        <TableCell>{{ leave.start_date }}</TableCell>
        <TableCell>{{ leave.end_date }}</TableCell>
        <TableCell>{{ leave.reason || "—" }}</TableCell>
        <TableCell>
          <Badge :class="badgeClass(leave.status)" class="capitalize">
            {{ leave.status }}
          </Badge>
        </TableCell>
        <TableCell v-if="isAdmin" class="text-right space-x-2">
          <template v-if="leave.status === 'pending'">
            <Button
              size="sm"
              variant="neutral"
              @click="updateStatus(leave.id, 'approved')"
            >
              Approve
            </Button>
            <Button
              size="sm"
              variant="neutral"
              class="bg-rose-600 text-white"
              @click="updateStatus(leave.id, 'rejected')"
            >
              Reject
            </Button>
          </template>
          <span v-else class="text-sm text-muted-foreground">—</span>
        </TableCell>
      </TableRow>
      <TableRow v-if="props.leaves.length === 0">
        <TableCell
          :colspan="isAdmin ? 7 : 5"
          class="text-center text-muted-foreground"
        >
          No leave requests found.
        </TableCell>
      </TableRow>
    </TableBody>
  </Table>
</template>
