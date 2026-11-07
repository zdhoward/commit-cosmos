#!/usr/bin/env python3
"""Commit Cosmos: turn the git history of your repos into one self-contained, interactive 3D HTML universe.

Each repo becomes a star, each commit an orbiting body, and the timeline replays your work.

Privacy: only aggregate metadata is read (timestamp, lines added/removed, file-type buckets).
Commit messages, file names, code and author identity are never read into the output.
Repo names are replaced by "Project 01..." unless you pass --names.

Usage:
  python commitcosmos.py                      # scan repos under the current directory
  python commitcosmos.py ~/code ~/work        # scan several roots
  python commitcosmos.py ~/code --names --title "My Year in Code" -o cosmos.html
  python commitcosmos.py ~/code --all-authors # include everyone's commits, not just yours

Requires Python 3.8+ and git. No third-party packages.
"""
import argparse
import collections
import datetime
import json
import os
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
THREE_URL = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"

CATS = ["code", "docs", "web", "data", "media", "other"]
EXT = {}
for cat, exts in {
    "code": "py js ts tsx jsx mjs rs cs cpp cc c h hpp go ps1 sh bat lua java kt swift rb php gd vue svelte",
    "docs": "md txt rst adoc",
    "web": "html htm css scss sass less",
    "data": "json yml yaml toml csv tsv sql xml ini cfg lock",
    "media": "png jpg jpeg svg gif webp wav mp3 ogg flac mp4 mov glb fbx psd",
}.items():
    for e in exts.split():
        EXT[e] = cat


def find_repos(roots, depth):
    seen = set()
    for root in roots:
        root = os.path.abspath(os.path.expanduser(root))
        base = root.rstrip(os.sep).count(os.sep)
        for dirpath, dirnames, _ in os.walk(root):
            if ".git" in dirnames or os.path.isfile(os.path.join(dirpath, ".git")):
                if dirpath not in seen:
                    seen.add(dirpath)
                    yield dirpath
                dirnames[:] = []
                continue
            dirnames[:] = [d for d in dirnames if d not in ("node_modules", ".venv", "venv", "__pycache__")]
            if dirpath.rstrip(os.sep).count(os.sep) - base >= depth:
                dirnames[:] = []


def git_user():
    try:
        return subprocess.run(["git", "config", "user.name"], capture_output=True, text=True).stdout.strip()
    except OSError:
        return ""


def read_repo(path, author):
    cmd = ["git", "-C", path, "log", "--no-merges", "--no-renames", "--numstat", "--format=@@%aI"]
    if author:
        cmd.insert(5, "--author=" + author)
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        return []
    rows, cur = [], None
    for line in r.stdout.splitlines():
        if line.startswith("@@"):
            if cur:
                rows.append(cur)
            try:
                dt = datetime.datetime.fromisoformat(line[2:])
            except ValueError:
                cur = None
                continue
            # local hour/day-of-week as the author experienced it
            cur = {"ts": int(dt.timestamp()), "h": dt.hour, "d": dt.weekday(), "a": 0, "r": 0,
                   "c": collections.Counter()}
        elif cur is not None and line.strip():
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            a = 0 if parts[0] == "-" else int(parts[0] or 0)
            d = 0 if parts[1] == "-" else int(parts[1] or 0)
            cur["a"] += a
            cur["r"] += d
            name = parts[2]
            ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
            cur["c"][EXT.get(ext, "other")] += a + d
    if cur:
        rows.append(cur)
    return rows


def build(args):
    author = None if args.all_authors else (args.author or git_user())
    if not args.all_authors and not author:
        sys.exit("No git user.name configured. Pass --author NAME or --all-authors.")
    roots = args.roots or ["."]
    repos, commits = [], []
    found = list(find_repos(roots, args.depth))
    if not found:
        sys.exit("No git repositories found under: " + ", ".join(roots))
    for path in sorted(found):
        rows = read_repo(path, author)
        if len(rows) < args.min_commits:
            continue
        rid = len(repos)
        for c in rows:
            commits.append([rid, c["ts"], c["a"], c["r"], c["h"], c["d"], [c["c"][k] for k in CATS]])
        repos.append({"n": os.path.basename(path), "k": len(rows)})
    if not commits:
        sys.exit("No commits matched (author filter: %r)." % author)
    # order repos by first commit so ids are chronological, then remap
    first = {}
    for c in commits:
        first[c[0]] = min(first.get(c[0], c[1]), c[1])
    order = sorted(range(len(repos)), key=lambda i: first[i])
    remap = {old: new for new, old in enumerate(order)}
    repos = [repos[i] for i in order]
    for c in commits:
        c[0] = remap[c[0]]
    commits.sort(key=lambda c: c[1])
    for i, r in enumerate(repos):
        r["n"] = r["n"] if args.names else "Project %02d" % (i + 1)
    return {"cats": CATS, "repos": repos, "commits": commits, "named": bool(args.names)}


def three_tag(inline):
    if not inline:
        return '<script src="%s"></script>' % THREE_URL
    with urllib.request.urlopen(THREE_URL, timeout=30) as resp:
        return "<script>" + resp.read().decode("utf-8") + "</script>"


def main():
    ap = argparse.ArgumentParser(description="Generate an interactive 3D universe from your git history.")
    ap.add_argument("roots", nargs="*", help="directories to scan for git repos (default: current directory)")
    ap.add_argument("-o", "--out", default="commit-cosmos.html", help="output HTML file")
    ap.add_argument("--title", default="Commit Cosmos", help="title shown in the scene")
    ap.add_argument("--author", help="only count commits whose author matches this (default: your git user.name)")
    ap.add_argument("--all-authors", action="store_true", help="count every author's commits")
    ap.add_argument("--names", action="store_true", help="include real repo names (default: anonymized)")
    ap.add_argument("--depth", type=int, default=2, help="how many folder levels below each root to search")
    ap.add_argument("--min-commits", type=int, default=3, help="skip repos with fewer matching commits")
    ap.add_argument("--inline-three", action="store_true", help="embed three.js so the file works offline")
    args = ap.parse_args()

    data = build(args)
    with open(os.path.join(HERE, "template.html"), encoding="utf-8") as f:
        html = f.read()
    payload = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    html = (html.replace("__THREE__", three_tag(args.inline_three))
                .replace("__TITLE__", args.title.replace("<", "&lt;"))
                .replace("/*__DATA__*/null", payload))
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html)
    span = (data["commits"][-1][1] - data["commits"][0][1]) // 86400
    print("%d repos, %d commits, %d days -> %s (%d KB)%s" % (
        len(data["repos"]), len(data["commits"]), span, args.out, os.path.getsize(args.out) // 1024,
        "" if args.names else "  [repo names anonymized]"))


if __name__ == "__main__":
    main()
