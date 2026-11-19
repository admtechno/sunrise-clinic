// "600.00" from the API becomes "₹600" on the screen.
export const rupees = (fee: string) =>
  Number(fee).toLocaleString("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  });

// Session 07: 1536 bytes become "1.5 KB" (1 KB = 1024 bytes, as Django counts).
export function fileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} bytes`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}
