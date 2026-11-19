// The hooks the screens use. A screen asks for doctors; it does not know about
// fetch, keys or caching.
import { useEffect } from "react";
import {
  keepPreviousData,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { api, type DoctorQuery } from "../api";
import { doctorKeys, specialityKeys } from "../api/keys.ts";

export function useDoctorList(query: DoctorQuery) {
  const queryClient = useQueryClient();
  const list = useQuery({
    queryKey: doctorKeys.list(query),
    queryFn: () => api.listDoctors(query),
    // while a new filter loads, keep showing the old rows
    placeholderData: keepPreviousData,
  });
  // Session 07: when this page has arrived and the API says there is a next
  // one, ask for it in the background, so that Next opens at once.
  const hasNext = Boolean(list.data?.next) && !list.isPlaceholderData;
  // a new object on every render; its text changes only when the query does
  const key = JSON.stringify(query);
  useEffect(() => {
    if (!hasNext) return;
    const next: DoctorQuery = { ...query, page: (query.page ?? 1) + 1 };
    void queryClient.prefetchQuery({
      queryKey: doctorKeys.list(next),
      queryFn: () => api.listDoctors(next),
    });
  }, [hasNext, key, queryClient]); // eslint-disable-line react-hooks/exhaustive-deps
  return list;
}

export function useDoctor(id: number) {
  return useQuery({
    queryKey: doctorKeys.detail(id),
    queryFn: () => api.getDoctor(id),
  });
}

export function useFreeSlots(id: number) {
  return useQuery({
    queryKey: doctorKeys.slots(id),
    queryFn: () => api.getFreeSlots(id),
  });
}

export function useSpecialities() {
  return useQuery({
    queryKey: specialityKeys.all,
    queryFn: () => api.listSpecialities(),
  });
}
