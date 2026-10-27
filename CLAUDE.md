# CLAUDE.md

## About me
I am Haseeb, a career switcher learning Python and AI engineering by building portfolio projects.
I must be able to explain every file and every line in a job interview, so teach as you build.
In explanations to me, never use the dash character.

## Source of truth
* PROJECT_SPEC.md defines the scope, stack, folder structure and milestones.
* If this file and PROJECT_SPEC.md seem to conflict, stop and ask me.

## Hard rules
1. Build only what is in PROJECT_SPEC.md. No extra features, endpoints, files or "nice to haves".
2. Never add a library, service or API, and never change the architecture or folder structure, without asking me first. Name it, say why, and wait for my yes.
3. If anything is unclear or missing, stop and ask. Never guess.
4. Never invent APIs, function names, model names, CLI flags or settings. Check the official docs first and give me the URL. If you cannot verify something, say "unverified" and ask.
5. Test first: write the test, run it and show it failing, write the code, run all tests and show them passing. Unit tests never call real external or paid APIs; mock them.
6. Work on one milestone at a time. Before coding, show a short plan for the current milestone and wait for my OK. At the end, stop and give me the End of Milestone Report (below). Never start the next milestone until I say so.
7. Explain each new concept in 3 sentences or fewer, in plain English, the first time it appears.
8. Make small commits, one logical change each, only after tests pass. Message format: "M2: add classifier fallback". Never push or force push without asking.

## Safety
* Secrets live only in .env (gitignored) or the cloud secret store. Never print, log, commit or read out key values.
* Ask before any command that deploys, can cost money, deletes files, changes cloud settings or installs global tools.
* Synthetic data only. No real customer data.

## Code style
* Python 3.12 with type hints, small functions, clear names, a one line docstring per function.
* Keep code simple enough for a beginner to read. Prefer the standard library.

## End of Milestone Report (use exactly these headings)
1. Summary: what was built, in 3 to 5 bullets
2. Files changed: list with one line each
3. What I should test: exact commands and the expected output
4. New concepts: each in 3 sentences or fewer
5. Quiz: 3 short questions to check I understand the code
6. What comes next: the next milestone name and goal (do not start it)
