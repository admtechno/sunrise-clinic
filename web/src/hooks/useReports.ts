// Session 07: the reports of one appointment, and the upload of a file.
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, type Report } from "../api";
import { reportKeys } from "../api/keys.ts";

export function useReports(appointmentId: number) {
  return useQuery({
    queryKey: reportKeys.list(appointmentId),
    queryFn: () => api.listReports(appointmentId),
  });
}

export function useUploadReport(appointmentId: number) {
  const queryClient = useQueryClient();
  const [progress, setProgress] = useState(0);
  const upload = useMutation({
    mutationFn: (file: File) => {
      setProgress(0);
      return api.uploadReport(appointmentId, file, file.name, setProgress);
    },
    // The answer IS the new report: add it to the cached list, no new request.
    onSuccess: (report) =>
      queryClient.setQueryData<Report[]>(
        reportKeys.list(appointmentId),
        (reports) => [...(reports ?? []), report],
      ),
  });
  return { upload, progress };
}
