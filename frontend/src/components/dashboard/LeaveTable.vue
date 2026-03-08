<script setup lang="ts">
import { ref } from "vue";
import { Loader2 } from "lucide-vue-next";
import { toast } from "vue-sonner";
import { format, parseISO } from "date-fns";
import api from "@/lib/api";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

// ── Types ───────────────────────────────────────────────────────────────────
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

// ── Date formatting helper ──────────────────────────────────────────────────
function formatDate(dateStr: string): string {
  try {
    return format(parseISO(dateStr), "MMM dd, yyyy");
  } catch {
    return dateStr;
  }
}

const props = defineProps<{
  leaves: LeaveRequest[];
  isAdmin: boolean;
}>();

const emit = defineEmits<{
  (e: "updated"): void;
}>();

// ── Loading state per leave (for Approve spinner) ───────────────────────────
const loadingId = ref<string | null>(null);

// ── Rejection dialog state ──────────────────────────────────────────────────
const rejectDialogOpen = ref(false);
const rejectLeaveId = ref<string | null>(null);
const rejectLeaveName = ref("");
const adminNote = ref("");
const isRejecting = ref(false);

function openRejectDialog(leave: LeaveRequest) {
  rejectLeaveId.value = leave.id;
  rejectLeaveName.value = leave.employee_name;
  adminNote.value = "";
  rejectDialogOpen.value = true;
}

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

// ── Approve (immediate) ─────────────────────────────────────────────────────
async function approveLeave(leaveId: string) {
  loadingId.value = leaveId;
  try {
    await api.patch(`/leaves/${leaveId}/status`, { status: "approved" });
    toast.success("Leave request approved");
    emit("updated");
  } catch (err: any) {
    const message = err.response?.data?.detail || "Failed to approve leave";
    toast.error("Approval failed", { description: message });
  } finally {
    loadingId.value = null;
  }
}

// ── Reject (via dialog confirmation) ────────────────────────────────────────
async function confirmRejection() {
  if (!rejectLeaveId.value) return;
  if (!adminNote.value.trim()) {
    toast.error("Reason required", {
      description: "Please provide a reason for rejection.",
    });
    return;
  }

  isRejecting.value = true;
  try {
    await api.patch(`/leaves/${rejectLeaveId.value}/status`, {
      status: "rejected",
      admin_note: adminNote.value.trim(),
    });
    toast.success("Leave request rejected");
    rejectDialogOpen.value = false;
    emit("updated");
  } catch (err: any) {
    const message = err.response?.data?.detail || "Failed to reject leave";
    toast.error("Rejection failed", { description: message });
  } finally {
    isRejecting.value = false;
  }
}
</script>

<template>
  <!-- ── Rejection Reason Dialog ─────────────────────────────────────────── -->
  <Dialog v-model:open="rejectDialogOpen">
    <DialogContent class="sm:max-w-md">
      <DialogHeader>
        <DialogTitle>Reject Leave Request</DialogTitle>
        <DialogDescription>
          Provide a reason for rejecting
          <strong>{{ rejectLeaveName }}</strong
          >'s leave request.
        </DialogDescription>
      </DialogHeader>

      <div class="space-y-2 py-2">
        <Textarea
          v-model="adminNote"
          placeholder="Reason for rejection…"
          rows="3"
        />
      </div>

      <DialogFooter class="gap-2 sm:gap-0">
        <Button variant="neutral" @click="rejectDialogOpen = false">
          Cancel
        </Button>
        <Button
          variant="default"
          class="bg-rose-600 ml-2 text-white hover:bg-rose-700"
          :disabled="isRejecting"
          @click="confirmRejection"
        >
          <Loader2 v-if="isRejecting" class="size-4 mr-2 animate-spin" />
          {{ isRejecting ? "Rejecting…" : "Confirm Rejection" }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>

  <!-- ── Leave Table ─────────────────────────────────────────────────────── -->
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
        <TableCell>{{ formatDate(leave.start_date) }}</TableCell>
        <TableCell>{{ formatDate(leave.end_date) }}</TableCell>
        <TableCell class="max-w-50">
          {{ leave.reason || "—" }}
        </TableCell>
        <TableCell>
          <TooltipProvider v-if="leave.status === 'rejected'">
            <Tooltip>
              <TooltipTrigger as-child>
                <Badge
                  :class="badgeClass(leave.status)"
                  class="capitalize cursor-default"
                >
                  {{ leave.status }}
                </Badge>
              </TooltipTrigger>
              <TooltipContent side="top" class="max-w-xs">
                {{ leave.admin_note || "No reason provided" }}
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
          <Badge v-else :class="badgeClass(leave.status)" class="capitalize">
            {{ leave.status }}
          </Badge>
        </TableCell>
        <TableCell v-if="isAdmin" class="text-right">
          <div
            v-if="leave.status === 'pending'"
            class="flex flex-wrap justify-end gap-2"
          >
            <Button
              size="sm"
              variant="neutral"
              :disabled="loadingId === leave.id"
              @click="approveLeave(leave.id)"
            >
              <Loader2
                v-if="loadingId === leave.id"
                class="size-4 mr-1 animate-spin"
              />
              Approve
            </Button>
            <Button
              size="sm"
              variant="neutral"
              class="bg-rose-600 text-white"
              @click="openRejectDialog(leave)"
            >
              Reject
            </Button>
          </div>
          <span v-else class="text-sm text-muted-foreground">—</span>
        </TableCell>
      </TableRow>
      <TableRow v-if="props.leaves.length === 0">
        <TableCell
          :colspan="isAdmin ? 7 : 6"
          class="text-center text-muted-foreground py-8"
        >
          No leave requests found.
        </TableCell>
      </TableRow>
    </TableBody>
  </Table>
</template>
