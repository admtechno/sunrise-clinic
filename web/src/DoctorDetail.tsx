import {
  Alert,
  Button,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Stack,
  Typography,
} from "@mui/material";
import { useNavigate, useParams } from "react-router";
import BookForm from "./BookForm";
import { useAuth } from "./auth/AuthProvider";
import { rupees } from "./format";
import { useDoctor, useFreeSlots } from "./hooks/useDoctors";

export default function DoctorDetail() {
  const id = Number(useParams().id); // /doctors/2 -> 2
  const navigate = useNavigate();
  const onBack = () => navigate("/");
  const doctor = useDoctor(id);
  const slots = useFreeSlots(id); // two queries, two cache entries
  const { me } = useAuth();

  return (
    <Stack spacing={2} sx={{ alignItems: "flex-start" }}>
      <Button onClick={onBack}>Back to the list</Button>
      {doctor.isPending && <CircularProgress aria-label="Loading doctor" />}
      {doctor.isError && <Alert severity="error">{doctor.error.message}</Alert>}
      {doctor.isSuccess && (
        <>
          <Typography variant="h5">{doctor.data.name}</Typography>
          <Typography>
            {doctor.data.speciality.name}, fee {rupees(doctor.data.fee)}.{" "}
            {doctor.data.bio}
          </Typography>
        </>
      )}
      <Typography variant="h6">Free slots</Typography>
      {slots.isPending && <CircularProgress aria-label="Loading free slots" />}
      {slots.isError && <Alert severity="error">{slots.error.message}</Alert>}
      {slots.isSuccess && slots.data.length === 0 && (
        <Typography>No free slots.</Typography>
      )}
      {slots.isSuccess && slots.data.length > 0 && (
        <List dense>
          {slots.data.map((slot) => (
            <ListItem key={slot.id}>
              <ListItemText primary={`${slot.date} at ${slot.start_time}`} />
            </ListItem>
          ))}
        </List>
      )}
      <Typography variant="h6">Book a visit</Typography>
      {me?.is_patient ? (
        <BookForm doctorId={id} slots={slots.data ?? []} />
      ) : (
        <Typography>Log in as a patient to book.</Typography>
      )}
    </Stack>
  );
}
