# Contributing

Thanks for wanting to help out. There's a few ways to contribute depending on how hands-on you want to be

This is a volunteer-run hobby project — maintainers work on it in their free time, so there's no guarantee every issue or PR gets a response or review. Don't take it personally if things sit for a while

## 1. Code changes

Fork the repo, make your changes, open a PR against `main`. A few things to keep in mind:

- Prioritize no new dependencies — the scripts are stdlib-only Python on purpose to keep it easy for anyone
- Match the existing style (tabs, same patterns as the current scripts)
- By submitting a PR, you agree your contribution is licensed under this project's [MIT License](LICENSE), same as the rest of the code

## 2. Suggestions without touching the code

Open an [Issue](../../issues) — a missing location, a wrong reward, a feature idea, whatever. No code or data required, just describe what you'd like to see

## 3. Database dump contributions

If you've filled in or corrected scouting data in your own database (e.g. transcribed more locations, fixed an existing entry), export it with [`export-db`](export-db/README.md) and open a PR or Issue with the dump attached

- Since this data is sourced from the [Frostpunk Wiki](https://frostpunk.fandom.com/wiki/Scouting), by contributing a dump you agree your changes are licensed under [CC BY-NC-SA](DATA_LICENSE.md) — same as the rest of the published data, **not** MIT
- Once reviewed, it'll be published as the latest dump under [Releases](../../releases)
