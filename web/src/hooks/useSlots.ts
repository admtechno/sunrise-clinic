// The slots of one doctor as reception sees them: list, create and delete.
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, type SlotInput } from "../api";
import { doctorKeys, slotKeys } from "../api/keys.ts";

export function useDoctorSlots(doctor: number) {
  const query = { doctor, page_size: 20 };
  return useQuery({
    queryKey: slotKeys.list(query),
    queryFn: () => api.listSlots(query),
  });
}

export function useCreateSlot() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: SlotInput) => api.createSlot(input),
    onSuccess: (slot) =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: slotKeys.all }),
        queryClient.invalidateQueries({
          queryKey: doctorKeys.slots(slot.doctor),
        }),
      ]),
  });
}

// Delete a slot. 204 has no body; 409 when it has appointments.
export function useDeleteSlot() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (slot: { id: number; doctor: number }) =>
      api.deleteSlot(slot.id),
    onSuccess: (_nothing, slot) =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: slotKeys.all }),
        queryClient.invalidateQueries({
          queryKey: doctorKeys.slots(slot.doctor),
        }),
      ]),
  });
}
