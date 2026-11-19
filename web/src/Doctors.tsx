// Session 07: the doctors list in pages. Filters, sort and page live in the
// address, so a reload, Back and a shared link show the same list.
import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import {
  Alert,
  AlertTitle,
  Box,
  Button,
  Chip,
  CircularProgress,
  MenuItem,
  Pagination,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from "@mui/material";
import { ApiError } from "./api";
import {
  ORDERINGS,
  PAGE_SIZE,
  readSearch,
  toQuery,
  writeSearch,
  type DoctorSearch,
} from "./doctors/searchParams.ts";
import { rupees } from "./format";
import { useDoctorList, useSpecialities } from "./hooks/useDoctors";

const ORDER_NAMES: Record<(typeof ORDERINGS)[number], string> = {
  name: "Name (A to Z)",
  "-name": "Name (Z to A)",
  fee: "Fee (low to high)",
  "-fee": "Fee (high to low)",
};

export default function Doctors() {
  const navigate = useNavigate();
  const [params, setParams] = useSearchParams();
  const search = readSearch(params); // the address is the state
  // a new filter or sort starts again at page 1
  const change = (patch: Partial<DoctorSearch>) =>
    setParams(writeSearch({ ...search, page: 1, ...patch }));
  const [text, setText] = useState(search.search ?? "");

  const doctors = useDoctorList(toQuery(search));
  const specialities = useSpecialities();
  const errorCode =
    doctors.error instanceof ApiError ? doctors.error.code : "UNKNOWN";
  const pages = doctors.data ? Math.ceil(doctors.data.count / PAGE_SIZE) : 0;

  return (
    <>
      <Stack spacing={2} sx={{ mb: 2, alignItems: "flex-start" }}>
        <ToggleButtonGroup
          size="small"
          exclusive
          value={search.speciality ?? "all"}
          onChange={(_event, value: string | null) =>
            value && change({ speciality: value === "all" ? undefined : value })
          }
        >
          <ToggleButton value="all">All</ToggleButton>
          {specialities.data?.map((s) => (
            <ToggleButton key={s.slug} value={s.slug}>
              {s.name}
            </ToggleButton>
          ))}
        </ToggleButtonGroup>
        <Stack direction="row" spacing={2} sx={{ alignItems: "center" }}>
          <TextField
            size="small"
            label="Search name"
            value={text}
            onChange={(event) => setText(event.target.value)}
          />
          <Button
            variant="outlined"
            onClick={() => change({ search: text.trim() || undefined })}
          >
            Search
          </Button>
          <TextField
            select
            size="small"
            label="Sort by"
            value={search.ordering}
            onChange={(event) =>
              change({
                ordering: event.target.value as DoctorSearch["ordering"],
              })
            }
            sx={{ minWidth: 190 }}
          >
            {ORDERINGS.map((o) => (
              <MenuItem key={o} value={o}>
                {ORDER_NAMES[o]}
              </MenuItem>
            ))}
          </TextField>
          {doctors.isFetching && !doctors.isPending && (
            <Chip size="small" label="Updating..." color="info" />
          )}
        </Stack>
      </Stack>

      {doctors.isPending && <CircularProgress aria-label="Loading doctors" />}

      {doctors.isError && (
        <Alert
          severity="error"
          action={
            <Button
              color="inherit"
              size="small"
              onClick={() => void doctors.refetch()}
            >
              Try again
            </Button>
          }
        >
          <AlertTitle>Could not load the doctors ({errorCode})</AlertTitle>
          {doctors.error.message}
        </Alert>
      )}

      {doctors.isSuccess && doctors.data.results.length === 0 && (
        <Typography>No doctors match your filters.</Typography>
      )}

      {doctors.isSuccess && doctors.data.results.length > 0 && (
        <Box>
          <Typography variant="subtitle1" sx={{ mb: 1 }}>
            Page {search.page} of {pages}, {doctors.data.count} doctors
          </Typography>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Doctor</TableCell>
                <TableCell>Speciality</TableCell>
                <TableCell align="right">Fee</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {doctors.data.results.map((doctor) => (
                <TableRow
                  key={doctor.id}
                  hover
                  sx={{ cursor: "pointer" }}
                  onClick={() => navigate(`/doctors/${doctor.id}`)}
                >
                  <TableCell>{doctor.name}</TableCell>
                  <TableCell>
                    <Chip size="small" label={doctor.speciality.name} />
                  </TableCell>
                  <TableCell align="right">{rupees(doctor.fee)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          {pages > 1 && (
            <Pagination
              sx={{ mt: 2 }}
              count={pages}
              page={search.page}
              onChange={(_event, page) =>
                setParams(writeSearch({ ...search, page }))
              }
            />
          )}
        </Box>
      )}
    </>
  );
}
