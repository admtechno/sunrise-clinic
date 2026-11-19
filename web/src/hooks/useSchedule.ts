// Session 06: the doctor's schedule and the Complete button.
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../api";
import { appointmentKeys, scheduleKeys } from "../api/keys.ts";

export function useSchedule(page = 1) {
  return useQuery({
    queryKey: scheduleKeys.list(page),
    queryFn: () => api.getSchedule(page),
  });
}

export function useCompleteAppointment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.completeAppointment(id),
    onSettled: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: scheduleKeys.all }),
        queryClient.invalidateQueries({ queryKey: appointmentKeys.all }),
      ]),
  });
}
