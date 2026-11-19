// Session 04: the mutations. A mutation sends a change; when it is done, the
// cached answers it made old are invalidated, so TanStack Query fetches them
// again.
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, type AppointmentPage, type BookingInput } from "../api";
import { appointmentKeys, doctorKeys } from "../api/keys.ts";

export function useMyAppointments(page = 1, enabled = true) {
  return useQuery({
    queryKey: appointmentKeys.list(page),
    queryFn: () => api.listAppointments(page),
    enabled, // only when somebody is signed in
  });
}

export function useBookAppointment(doctorId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: BookingInput) => api.bookAppointment(input),
    // after a success AND after a failure: a 400 "already booked" also means
    // that our list of free slots is old
    onSettled: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: doctorKeys.slots(doctorId) }),
        queryClient.invalidateQueries({ queryKey: appointmentKeys.all }),
      ]),
  });
}

// Optimistic: the row says "cancelled" at once; if the API says no, the old
// rows come back (rollback). Either way the list is fetched again at the end.
export function useCancelAppointment({ optimistic = true } = {}) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.cancelAppointment(id),
    onMutate: async (id: number) => {
      if (!optimistic) return { before: [] };
      // stop a refetch that is running, or its old answer would overwrite ours
      await queryClient.cancelQueries({ queryKey: appointmentKeys.all });
      const before = queryClient.getQueriesData<AppointmentPage>({
        queryKey: appointmentKeys.all,
      });
      queryClient.setQueriesData<AppointmentPage>(
        { queryKey: appointmentKeys.all },
        (page) =>
          page && {
            ...page,
            results: page.results.map((a) =>
              a.id === id ? { ...a, status: "cancelled" as const } : a,
            ),
          },
      );
      return { before }; // handed to onError
    },
    onError: (_error, _id, context) => {
      for (const [key, page] of context?.before ?? []) {
        queryClient.setQueryData(key, page); // rollback
      }
    },
    onSettled: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: appointmentKeys.all }),
        // the free slots of every doctor
        queryClient.invalidateQueries({ queryKey: doctorKeys.all }),
      ]),
  });
}
