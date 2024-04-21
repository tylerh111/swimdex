# Swimdex

![version-badge](https://img.shields.io/badge/version-0.1-blue)

> Codex for Swim Strokes

[Swimdex](https://tylerh111.github.io/swimdex) is a collection of information about the swim strokes used in both competitive and recreational swimming.

## Developing

Swimdex uses [`mkdocs`](https://www.mkdocs.org/) and [`nox`](https://nox.thea.codes/en/stable/) for development.
Use the following to install the necessary tools.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.in
pip install -r requirements/build.in
```

### Building Documentation

Swimdex can be built locally for development.
Use the following to build the site.

```bash
mkdocs build
mkdocs serve # to view locally
```

### Releasing Documentation

Swimdex is updated by simply pushing to the docs branch.
Use the following to release the site.
Note, extra command line arguments cannot be used when running multiple sessions.

```bash
nox -s version bump build release
nox -s version bump build release -- --help
```
