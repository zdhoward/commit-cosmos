# Commit Cosmos

Turn the git history of all your repos into one self-contained, interactive 3D universe.

- Each **repo** is a star; its size grows with every commit.
- Each **commit** is a body orbiting its star. Orbit radius reflects lines changed; color reflects the **hour of day** you made it.
- A scrubbable **timeline** replays your work. Idle gaps are compressed so playback never sits in the dark.
- A **weekly rhythm** grid (Mon-Sun x 24h) fills in as time advances.
- Drag to orbit, scroll to zoom, hover a star for details, `space` play/pause, `t` toggle the auto-tour.

## Use

```
python commitcosmos.py ~/code                       # scan repos under a folder
python commitcosmos.py ~/code ~/work --names --title "My Year in Code" -o cosmos.html
python commitcosmos.py ~/code --inline-three        # embed three.js: works fully offline
```

Open the resulting HTML file in any modern browser. Needs Python 3.8+ and git; no packages.

| Flag | Meaning |
|---|---|
| `--names` | show real repo names (default: "Project 01", "Project 02", ...) |
| `--author NAME` | only commits whose author matches NAME (default: your `git config user.name`) |
| `--all-authors` | count everyone's commits |
| `--depth N` | folder levels to search below each root (default 2) |
| `--min-commits N` | skip repos with fewer matching commits (default 3) |
| `--title TEXT` | title in the scene |

## Privacy

The generator reads only commit timestamps (with your local hour and weekday), lines added/removed, and file-type buckets.
It never reads commit messages, file names, code or author identity into the output. Repo names are anonymized unless you pass `--names`.
The output HTML embeds the data, so share it only if you are comfortable with that activity pattern being public.
This repo's `.gitignore` excludes generated HTML so your own output is never committed here.
