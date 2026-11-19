// Session 07: one appointment, for the heading of the Reports screen.
import { useQuery } from "@tanstack/react-query";
import { api } from "../api";

export function useAppointment(id: number) {
  return useQuery({
    queryKey: ["appointments", "detail", id],
    queryFn: () => api.getAppointment(id),
  });
}
