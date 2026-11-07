# Commit Cosmos

Turns the git history of your repos into a single HTML file you can open in a browser. Every repo is a star. Every commit orbits its star. A timeline replays the whole thing.

**[Live demo](https://zdhoward.github.io/commit-cosmos/examples/demo.html)** (fake data, 14 made-up repos)

It's a Python script plus an HTML template. No build step, no dependencies beyond git and Python 3.8.

## Quick start

```
python commitcosmos.py ~/code
```

That scans `~/code` for git repos, reads your commits, and writes `commit-cosmos.html`. Open it.

A few more examples:

```
# several folders, real repo names, custom title
python commitcosmos.py ~/code ~/work --names --title "2025 in code" -o cosmos.html

# work offline (embeds three.js, adds about 600 KB)
python commitcosmos.py ~/code --inline-three

# count everyone's commits, not just yours
python commitcosmos.py ~/code --all-authors
```

## What you're looking at

- **Star size** grows with the number of commits in that repo so far.
- **Orbiting dots** are commits. A wider orbit means more lines changed.
- **Dot color** is the hour of day you made the commit, midnight to midnight.
- **The grid in the corner** is your week: Monday to Sunday by hour, filling in as time plays.
- **Quiet stretches** longer than nine days are squeezed to nine, so the replay doesn't sit in the dark. The date shown is the real one.

Controls: drag to orbit, scroll to zoom, click a star to focus on it, `Esc` to zoom back out, `Space` to play or pause, `T` to toggle the slow camera tour. Hovering a star shows its name and commit count.

## Options

| Flag | What it does |
|---|---|
| `--names` | Show real repo names. Default is "Project 01", "Project 02", and so on. |
| `--author NAME` | Only count commits whose author matches NAME. Default is your `git config user.name`. |
| `--all-authors` | Count every author. |
| `--depth N` | How many folder levels to search under each root. Default 2. |
| `--min-commits N` | Skip repos with fewer matching commits. Default 3. |
| `--title TEXT` | Title shown in the scene. |
| `--inline-three` | Embed three.js so the file works with no network. |
| `-o FILE` | Output path. Default `commit-cosmos.html`. |

Merge commits and renames are ignored. Commits are matched by author name, so if you commit under several names, run it once per name or use `--all-authors`.

## Privacy

The script reads, per commit: the timestamp (with your local hour and weekday), lines added and removed, and a rough file-type split (code, docs, web, data, media, other). It does not read commit messages, file names, file contents, or author names and emails into the output.

Repo names are replaced unless you pass `--names`.

The HTML file contains all of that data inline. Before you share one, remember it shows when you work, how often, and how big your commits are. If that's fine, share away. If you're unsure, generate it without `--names` and look at it first.

## Try it without your own repos

```
python examples/make_sample.py
```

This builds a temporary folder of fake repos with a fake author, renders `examples/demo.html` from them, and deletes the folder. It's how the live demo was made.

## Limits

- three.js loads from a CDN unless you use `--inline-three`.
- Tested up to about 7,000 commits across 14 repos and about 3,600 across 51. Much larger histories may feel slow on weak GPUs.
- Needs WebGL. I've only tried it in a Chromium-based desktop browser. There's a small-screen layout, but I haven't tested it on a phone.
- It reads local clones only. Squash-merged or force-pushed history shows up as it exists on disk.

## How it works

`commitcosmos.py` shells out to `git log --numstat`, collapses the result into a small JSON blob, and drops it into `template.html`. The template is one file of plain JavaScript and a few shaders on top of three.js (r128). Commits are a single point cloud whose orbits are computed on the GPU, which is why thousands of them stay smooth.

## License

MIT. See `LICENSE`.
