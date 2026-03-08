<script setup lang="ts">
import { ref } from "vue";
import { useForm } from "vee-validate";
import { toTypedSchema } from "@vee-validate/zod";
import { z } from "zod";
import { format } from "date-fns";
import { type DateValue, getLocalTimeZone } from "@internationalized/date";
import { CalendarIcon, Loader2 } from "lucide-vue-next";
import { toast } from "vue-sonner";
import api from "@/lib/api";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { cn } from "@/lib/utils";

const emit = defineEmits<{
  (e: "submitted"): void;
}>();

// ── Zod schema with refine ──────────────────────────────────────────────────
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

const { handleSubmit, resetForm, setFieldValue, values } = useForm({
  validationSchema: leaveSchema,
  initialValues: {
    type: "casual",
    start_date: "",
    end_date: "",
    reason: "",
  },
});

const isSubmitting = ref(false);

// ── DateValue helpers ───────────────────────────────────────────────────────
function dateValueToString(dateValue: DateValue): string {
  const jsDate = dateValue.toDate(getLocalTimeZone());
  return format(jsDate, "yyyy-MM-dd");
}

function formatDisplay(dateStr: string): string {
  if (!dateStr) return "";
  const parts = dateStr.split("-").map(Number);
  const y = parts[0]!;
  const m = parts[1]!;
  const d = parts[2]!;
  return format(new Date(y, m - 1, d), "PPP");
}

const startDateValue = ref<DateValue | undefined>();
const endDateValue = ref<DateValue | undefined>();

function onStartDateSelect(selected: DateValue) {
  startDateValue.value = selected;
  setFieldValue("start_date", dateValueToString(selected));
}

function onEndDateSelect(selected: DateValue) {
  endDateValue.value = selected;
  setFieldValue("end_date", dateValueToString(selected));
}

// ── Submit ──────────────────────────────────────────────────────────────────
const onSubmit = handleSubmit(async (vals) => {
  isSubmitting.value = true;
  try {
    await api.post("/leaves/apply", {
      type: vals.type,
      start_date: vals.start_date,
      end_date: vals.end_date,
      reason: vals.reason,
    });
    toast.success("Leave applied successfully!");
    resetForm();
    startDateValue.value = undefined;
    endDateValue.value = undefined;
    emit("submitted");
  } catch (err: any) {
    const message = err.response?.data?.detail || "Failed to apply for leave";
    toast.error("Leave application failed", { description: message });
  } finally {
    isSubmitting.value = false;
  }
});
</script>

<template>
  <form class="grid gap-4 sm:grid-cols-2" @submit="onSubmit">
    <!-- Leave Type -->
    <FormField v-slot="{ componentField }" name="type">
      <FormItem class="space-y-2">
        <FormLabel class="mb-4">Leave Type</FormLabel>
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

    <!-- Start Date -->
    <FormField name="start_date">
      <FormItem class="space-y-2">
        <FormLabel>Start Date</FormLabel>
        <Popover>
          <PopoverTrigger as-child>
            <FormControl>
              <Button
                variant="noShadow"
                :class="
                  cn(
                    'w-full  justify-start text-left font-normal',
                    !values.start_date && 'text-muted-foreground',
                  )
                "
              >
                <CalendarIcon class="mr-2 size-4" />
                {{
                  values.start_date
                    ? formatDisplay(values.start_date)
                    : "Pick a date"
                }}
              </Button>
            </FormControl>
          </PopoverTrigger>
          <PopoverContent class="w-auto p-0">
            <Calendar
              :model-value="startDateValue"
              initial-focus
              @update:model-value="
                (v: any) => {
                  if (v) onStartDateSelect(v);
                }
              "
            />
          </PopoverContent>
        </Popover>
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- End Date — Popover + Calendar -->
    <FormField name="end_date">
      <FormItem class="space-y-2">
        <FormLabel>End Date</FormLabel>
        <Popover>
          <PopoverTrigger as-child>
            <FormControl>
              <Button
                variant="noShadow"
                :class="
                  cn(
                    'w-full justify-start text-left font-normal',
                    !values.end_date && 'text-muted-foreground',
                  )
                "
              >
                <CalendarIcon class="mr-2 size-4" />
                {{
                  values.end_date
                    ? formatDisplay(values.end_date)
                    : "Pick a date"
                }}
              </Button>
            </FormControl>
          </PopoverTrigger>
          <PopoverContent class="w-auto p-0">
            <Calendar
              :model-value="endDateValue"
              initial-focus
              @update:model-value="
                (v: any) => {
                  if (v) onEndDateSelect(v);
                }
              "
            />
          </PopoverContent>
        </Popover>
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Reason -->
    <FormField v-slot="{ componentField }" name="reason">
      <FormItem class="space-y-2 sm:col-span-2">
        <FormLabel class="mb-3">Reason</FormLabel>
        <FormControl>
          <Textarea
            placeholder="Brief reason for leave"
            v-bind="componentField"
            class="min-h-20"
          />
        </FormControl>
        <FormMessage />
      </FormItem>
    </FormField>

    <div class="sm:col-span-2">
      <Button type="submit" :disabled="isSubmitting">
        <Loader2 v-if="isSubmitting" class="size-4 mr-2 animate-spin" />
        {{ isSubmitting ? "Submitting…" : "Submit Request" }}
      </Button>
    </div>
  </form>
</template>
