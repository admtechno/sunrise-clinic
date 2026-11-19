// Session 14: waits until the API says it is ready to work.
//   node scripts/wait_for_ready.mjs [address] [seconds]
// Asks the address once a second and prints a line each time the answer
// changes. Exit code 0 on 200 {"status":"ready"}; 1 when the time is up.
// Used after a deploy (Session 17) and in the pipeline (Session 19).
const url = process.argv[2] ?? "http://127.0.0.1:8000/ready/";
const seconds = Number(process.argv[3] ?? 30);
const started = Date.now();
const elapsed = () => Math.round((Date.now() - started) / 1000);
let last = "";
while (elapsed() < seconds) {
  let now;
  try {
    const answer = await fetch(url, { signal: AbortSignal.timeout(3000) });
    const body = await answer.json().catch(() => ({}));
    if (answer.status === 200 && body.status === "ready") {
      console.log(`ready: ${answer.status} ${JSON.stringify(body)}`);
      process.exit(0);
    }
    now = `not ready: ${answer.status} ${JSON.stringify(body)}`;
  } catch (error) {
    now = `no answer (${error.cause?.code ?? error.name})`;
  }
  if (now !== last) console.log(now); // only the changes, not every try
  last = now;
  await new Promise((resolve) => setTimeout(resolve, 1000));
}
console.log(`not ready after ${seconds} seconds`);
process.exit(1);
