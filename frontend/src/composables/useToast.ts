import { ref } from "vue";

export interface Toast {
  id: number;
  message: string;
  type: "success" | "error";
}

const toasts = ref<Toast[]>([]);
let toastId = 0;

export function useToast() {
  const showToast = (
    message: string,
    type: "success" | "error" = "success",
  ) => {
    const id = ++toastId;
    toasts.value.push({ id, message, type });

    setTimeout(() => {
      toasts.value = toasts.value.filter((t) => t.id !== id);
    }, 3000);
  };

  return { toasts, showToast };
}
