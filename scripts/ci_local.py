"""Module 9, Session 19: a small model of a GitHub Actions run, to try the
workflow on your PC before you push. Not GitHub: only what this project uses.
    python scripts/ci_local.py [--job NAME] [--quiet]     (in the project folder)
Like GitHub it starts from the last COMMIT (git archive HEAD), not from the
files on your disk. Each job's services run in Docker with their ports on
127.0.0.1; a job with setup-python or setup-node runs its steps in the
python:<version>-slim or node:<version>-slim image; any other job runs on
this PC, as on a runner machine. Other `uses:` steps are skipped and named.
Needs Docker, Git and PyYAML (pip install -r scripts/requirements-ci.txt)."""
import argparse
import io
import os
import re
import shlex
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

import yaml

KEEP = ("HTTPS_PROXY", "HTTP_PROXY", "NO_PROXY", "https_proxy", "http_proxy")


def sh(*args, **kw):
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)


def expand(text, ports):
    """${{ job.services.<id>.ports['5432'] }} and ${{ github.* }} only."""
    def one(m):
        expr = m.group(1).strip()
        p = re.fullmatch(r"job\.services\.(\w+)\.ports\[['\"]?(\d+)['\"]?\]",
                         expr)
        if p:
            return ports[p.group(1)][p.group(2)]
        if expr.startswith("github."):
            return {"github.ref": "refs/heads/main", "github.event_name": "push",
                    "github.sha": sh("git", "rev-parse", "HEAD").stdout.strip()
                    }.get(expr, "")
        sys.exit(f"ci_local: cannot read the expression {expr!r}")
    return re.sub(r"\$\{\{(.*?)\}\}", one, str(text))


def start_services(name, job):
    ports, ids = {}, []
    for sid, svc in (job.get("services") or {}).items():
        cmd = ["docker", "run", "-d", "--name", f"ci-{name}-{sid}"]
        for k, v in (svc.get("env") or {}).items():
            cmd += ["-e", f"{k}={v}"]
        for p in svc.get("ports") or []:
            inner = str(p).split(":")[-1]
            cmd += ["-p", f"127.0.0.1::{inner}"]
        cmd += shlex.split(svc.get("options", "")) + [svc["image"]]
        sh("docker", "rm", "-f", f"ci-{name}-{sid}")
        cid = sh(*cmd).stdout.strip()
        ids.append(cid)
        ports[sid] = {}
        for p in svc.get("ports") or []:
            inner = str(p).split(":")[-1]
            out = sh("docker", "port", cid, f"{inner}/tcp").stdout.split("\n")[0]
            ports[sid][inner] = out.rsplit(":", 1)[-1]
        for _ in range(120):                        # wait for its health check
            state = sh("docker", "inspect", "-f", "{{.State.Health.Status}}", cid)
            if state.stdout.strip() in ("healthy", "<no value>", ""):
                break
            time.sleep(1)
        print(f"  service {sid}: {svc['image']}, healthy")
    return ports, ids


def run_job(name, job, env0, src, quiet):
    print(f"job {name}: {job.get('name', name)}")
    ports, services = start_services(name, job)
    work = Path(tempfile.mkdtemp(prefix=f"ci-{name}-"))
    with tarfile.open(fileobj=io.BytesIO(src)) as tar:       # actions/checkout
        tar.extractall(work, filter="data")
    image, cache = None, []
    for step in job["steps"]:
        uses = step.get("uses", "")
        with_ = step.get("with") or {}
        if uses.startswith("actions/setup-python"):
            image = f"python:{with_['python-version']}-slim"
            if with_.get("cache"):                 # a volume plays the cache
                cache = ["-v", "ci-local-pip:/root/.cache/pip"]
        if uses.startswith("actions/setup-node"):
            image = f"node:{with_['node-version']}-slim"
            if with_.get("cache"):
                cache = ["-v", "ci-local-npm:/root/.npm"]
    box = None
    if image:
        box = sh("docker", "run", "-d", "--rm", "--network", "host", *cache,
                 "-v", f"{work}:/github/workspace", "-w", "/github/workspace",
                 image, "sleep", "infinity").stdout.strip()
    env = {**env0}
    for k, v in (job.get("env") or {}).items():
        env[k] = expand(v, ports)
    run_defaults = (job.get("defaults") or {}).get("run") or {}
    wd = run_defaults.get("working-directory", ".")
    masks, ok = [], True
    try:
        for step in job["steps"]:
            label = step.get("name") or step.get("uses") or step["run"]
            if "run" not in step:
                known = ("actions/checkout", "actions/setup-python",
                         "actions/setup-node")
                done = step["uses"].startswith(known)
                print(f"  {'done' if done else 'skipped (GitHub only)'}: {label}")
                continue
            if not ok and "always()" not in str(step.get("if", "")):
                print(f"  not run: {label}")
                continue
            senv = {**env}
            for k, v in (step.get("env") or {}).items():
                senv[k] = expand(v, ports)
            senv["GITHUB_ENV"] = ("/github/workspace/.github_env" if box
                                  else str(work / ".github_env"))
            script = expand(step["run"], ports)
            sdir = step.get("working-directory", wd)
            if box:
                flags = [x for k, v in senv.items() for x in ("-e", f"{k}={v}")]
                where = f"/github/workspace/{sdir}"
                cmd = ["docker", "exec", *flags, "-w", where, box,
                       "bash", "-eo", "pipefail", "-c", script]
                result = sh(*cmd)
            else:
                result = sh("bash", "-eo", "pipefail", "-c", script,
                            cwd=work / sdir, env={**os.environ, **senv})
            out = result.stdout + result.stderr
            for line in out.splitlines():
                if line.startswith("::add-mask::"):
                    masks.append(line[len("::add-mask::"):])
            genv = work / ".github_env"
            if genv.exists():                    # values for the later steps
                for line in genv.read_text().splitlines():
                    if "=" in line:
                        k, v = line.split("=", 1)
                        env[k] = v
            for m in masks:
                out = out.replace(m, "***")
            shown = [x for x in out.splitlines()
                     if not x.startswith("::add-mask::")]
            passed = result.returncode == 0
            ok = ok and passed
            code = result.returncode
            status = "passed" if passed else f"FAILED (exit code {code})"
            print(f"  {status}: {label}")
            if not quiet or not passed:
                for line in shown[-8 if passed else -25:]:
                    print(f"    | {line}")
    finally:
        if box:
            sh("docker", "rm", "-f", box)
        for cid in services:
            sh("docker", "rm", "-f", cid)
        if image:                       # files made as root inside the container
            sh("docker", "run", "--rm", "-v", f"{work}:/w", image,
               "rm", "-rf", "/w")
        sh("rm", "-rf", str(work))
    print(f"job {name}: {'passed' if ok else 'FAILED'}")
    return ok


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workflow", default=".github/workflows/ci.yml")
    parser.add_argument("--job", action="append")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    flow = yaml.safe_load(Path(args.workflow).read_text())
    src = subprocess.run(["git", "archive", "--format=tar", "HEAD"],
                         capture_output=True, check=True).stdout
    env0 = {k: os.environ[k] for k in KEEP if k in os.environ}
    env0.update({k: str(v) for k, v in (flow.get("env") or {}).items()})
    env0["CI"] = "true"
    results = {}
    for name, job in flow["jobs"].items():
        if args.job and name not in args.job:
            continue
        needs = job.get("needs") or []
        needs = [needs] if isinstance(needs, str) else needs
        if any(not results.get(n, False) for n in needs):
            print(f"job {name}: skipped, because {', '.join(needs)} did not pass")
            results[name] = False
            continue
        results[name] = run_job(name, job, env0, src, args.quiet)
    print("workflow: " + ("passed" if all(results.values()) else "FAILED"))
    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
