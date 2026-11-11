# Coding-agent skills

The directories here are the shared source of coding-agent skills. The initial
selection is adapted from the ChitraguptaSutra skills collection: architecture
review, architectural decision records, code review, test-driven development,
and Python engineering. The Python skill has been adapted to this project.
The `graphify` skill and its references are bundled from the installed Graphify
0.9.95 package, from https://github.com/Graphify-Labs/graphify. The Graphify CLI
must be installed separately (the official Python package is `graphifyy`).

Run `python3 scripts/sync_skills.py` to create agent-specific references, and
`python3 scripts/sync_skills.py --verify` to check them. Use `--dry-run` to
preview changes, `--agents` to select targets, and `--help` for other options.
Edit the source under `skills/`, not the generated references. OpenSpec skills
and further Python, security, and Electron skills can be adopted as needed.
