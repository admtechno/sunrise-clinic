// The login page. The password goes to the API once and is not kept: the answer
// is an access token (memory) and the refresh cookie (HttpOnly).
import { useState } from "react";
import {
  Alert,
  Button,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useMutation } from "@tanstack/react-query";
import { useLocation, useNavigate } from "react-router";
import { ApiError } from "./api";
import { useAuth } from "./auth/AuthProvider";

// the API's answer in words for the person at the desk
function loginMessage(error: Error): string {
  if (error instanceof ApiError && error.code === "no_active_account") {
    return "Wrong username or password.";
  }
  if (error instanceof ApiError && error.status === 429) {
    return `Too many attempts. ${error.message}`; // "... available in 59 seconds."
  }
  return error.message;
}

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  // where the person wanted to go before the guard sent them here
  const from = (useLocation().state as { from?: string } | null)?.from ?? "/";
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const attempt = useMutation({
    mutationFn: () => login(username, password),
    onSuccess: () => {
      setPassword("");
      navigate(from, { replace: true });
    },
  });

  return (
    <Paper variant="outlined" sx={{ p: 3, maxWidth: 420 }}>
      <Stack
        component="form"
        spacing={2}
        onSubmit={(e) => {
          e.preventDefault();
          if (!attempt.isPending) attempt.mutate();
        }}
      >
        <Typography variant="h5">Log in</Typography>
        <TextField
          label="Username"
          autoComplete="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <TextField
          label="Password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        {attempt.isError && (
          <Alert severity="error">{loginMessage(attempt.error)}</Alert>
        )}
        <Button type="submit" variant="contained" disabled={attempt.isPending}>
          {attempt.isPending ? "Logging in..." : "Log in"}
        </Button>
      </Stack>
    </Paper>
  );
}
