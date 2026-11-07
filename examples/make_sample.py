#!/usr/bin/env python3
"""Build a throwaway folder of fake git repos (fake author, fake names) and render a demo from it.

Nothing here touches your real repos. Run from the project root:
    python examples/make_sample.py            # writes examples/demo.html
"""
import datetime
import os
import random
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
AUTHOR = "Demo Dev <demo@example.com>"
TZ = "-0500"
NAMES = ["orbit-api", "paper-cranes", "tidepool", "lantern-ui", "gravel", "night-market",
         "kiln", "quiet-hours", "moth-lamp", "signal-fox", "wayfinder", "cobalt-notes",
         "driftwood", "field-guide"]
EXTS = ["py", "py", "py", "js", "ts", "md", "css", "json", "html", "png"]


def stream(rng, start, end, weight):
    """Yield a git fast-import stream for one repo with commits clustered in bursts."""
    out = []
    t = start
    n = 0
    while t < end:
        # bursts: a few days of work, then a quiet stretch
        for _ in range(rng.randint(2, 6)):
            for _ in range(rng.choice([0, 1, 2, 3, 5, 8]) * weight):
                hour = int(rng.gauss(21, 3.5)) % 24 if rng.random() < .7 else rng.randint(9, 17)
                ts = int(t.replace(hour=hour, minute=rng.randint(0, 59)).timestamp())
                n += 1
                path = "src/f%d.%s" % (rng.randint(0, 40), rng.choice(EXTS))
                body = "\n".join("line %d" % i for i in range(max(1, min(3000, int(rng.paretovariate(0.9) * 12)))))
                msg = "work %d" % n
                out.append("commit refs/heads/main\nauthor %s %d %s\ncommitter %s %d %s\ndata %d\n%s\n"
                           % (AUTHOR, ts, TZ, AUTHOR, ts, TZ, len(msg), msg))
                out.append("M 100644 inline %s\ndata %d\n%s\n\n" % (path, len(body), body))
            t += datetime.timedelta(days=1)
        t += datetime.timedelta(days=int(rng.expovariate(1 / 6)))
    return "".join(out).encode()


def main():
    rng = random.Random(7)
    tmp = tempfile.mkdtemp(prefix="cosmos-sample-")
    try:
        origin = datetime.datetime(2023, 9, 1)
        for i, name in enumerate(NAMES):
            repo = os.path.join(tmp, name)
            subprocess.run(["git", "init", "-q", repo], check=True)
            start = origin + datetime.timedelta(days=int(i * 38 + rng.randint(0, 20)))
            end = start + datetime.timedelta(days=rng.randint(120, 420))
            data = stream(rng, start, min(end, datetime.datetime(2025, 9, 1)), rng.choice([1, 1, 2, 3]))
            subprocess.run(["git", "-C", repo, "fast-import", "--quiet"], input=data, check=True)
        out = os.path.join(HERE, "demo.html")
        subprocess.run([sys.executable, os.path.join(ROOT, "commitcosmos.py"), tmp, "--names",
                        "--author", "Demo Dev", "--title", "Demo Cosmos", "-o", out], check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
