// Session 07: the reports of one appointment. The patient uploads files; the
// patient and the doctor see the list.
import { useState } from "react";
import { useParams } from "react-router";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  LinearProgress,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { ApiError } from "./api";
import { useAuth } from "./auth/AuthProvider";
import { canUploadReports, isRole } from "./auth/roles.ts";
import ErrorAlert, { errorText } from "./ErrorAlert";
import { fileSize } from "./format";
import { checkReport, REPORT_TYPES } from "./forms/reportFile.ts";
import { useAppointment } from "./hooks/useAppointment";
import { useReports, useUploadReport } from "./hooks/useReports";

export default function AppointmentReports() {
  const id = Number(useParams().id);
  const { me } = useAuth();
  const role = me && isRole(me.role) ? me.role : null;
  const appointment = useAppointment(id);
  const reports = useReports(id);
  const { upload, progress } = useUploadReport(id);
  const [file, setFile] = useState<File | null>(null);
  const [problem, setProblem] = useState<string | null>(null);

  function choose(chosen: File | null) {
    upload.reset();
    setFile(chosen);
    setProblem(chosen ? checkReport(chosen) : null);
  }

  // A 400 names what is wrong with the file under fields.file.
  const fileErrors =
    upload.error instanceof ApiError ? (upload.error.fields.file ?? []) : [];

  return (
    <Stack spacing={2}>
      <Typography variant="h5">Reports</Typography>
      {appointment.isSuccess && (
        <Typography>
          {appointment.data.slot.doctor}, {appointment.data.slot.date} at{" "}
          {appointment.data.slot.start_time}, {appointment.data.patient}
        </Typography>
      )}
      {appointment.isError && <ErrorAlert error={appointment.error} />}

      {reports.isPending && <CircularProgress aria-label="Loading reports" />}
      {reports.isError && <ErrorAlert error={reports.error} />}
      {reports.isSuccess && reports.data.length === 0 && (
        <Typography>No reports yet.</Typography>
      )}
      {reports.isSuccess && reports.data.length > 0 && (
        <Table size="small" aria-label="Reports">
          <TableHead>
            <TableRow>
              <TableCell>File</TableCell>
              <TableCell align="right">Size</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {reports.data.map((r) => (
              <TableRow key={r.id}>
                <TableCell>{r.original_name}</TableCell>
                <TableCell align="right">{fileSize(r.size)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      {canUploadReports(role) && (
        <Box component="section" aria-label="Upload a report">
          <Typography variant="h6">Upload a report</Typography>
          <Typography variant="body2" sx={{ mb: 1 }}>
            PDF, JPG or PNG, at most 2 MB.
          </Typography>
          <Stack direction="row" spacing={2} sx={{ alignItems: "center" }}>
            <Button variant="outlined" component="label">
              Choose file
              <input
                hidden
                type="file"
                accept={REPORT_TYPES.join(",")}
                onChange={(event) => choose(event.target.files?.[0] ?? null)}
              />
            </Button>
            <Typography>{file ? file.name : "No file chosen"}</Typography>
            <Button
              variant="contained"
              disabled={!file || Boolean(problem) || upload.isPending}
              onClick={() => file && upload.mutate(file)}
            >
              Upload
            </Button>
          </Stack>
          {problem && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              {problem}
            </Alert>
          )}
          {upload.isPending && (
            <Box sx={{ mt: 2 }}>
              <LinearProgress variant="determinate" value={progress} />
              <Typography variant="body2">Uploading... {progress}%</Typography>
            </Box>
          )}
          {upload.isSuccess && (
            <Alert severity="success" sx={{ mt: 2 }}>
              {upload.data.original_name} uploaded.
            </Alert>
          )}
          {upload.isError && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {fileErrors.length > 0
                ? fileErrors.join(" ")
                : errorText(upload.error)}
            </Alert>
          )}
        </Box>
      )}
    </Stack>
  );
}
