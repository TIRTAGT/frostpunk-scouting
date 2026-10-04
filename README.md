# Frostpunk Scouting Database

A small set of tools to help visualize [Frostpunk](https://frostpunkgame.com/) scouting locations, discoveries and rewards

**[View the latest scouting cheatsheet](https://tirtagt.github.io/frostpunk-scouting/)**

> **Disclaimer**<br>
> This is an unofficial fan project. Not affiliated with, endorsed by, or sponsored by 11 bit studios (Frostpunk) or Fandom

> **AI disclosure**<br>
> This codebase was **mostly** built with AI assistance (Claude Opus 5.5)

## Available tools
| Tool | Purpose |
|------|---------|
| [`export-db`](export-db/README.md) | Performs a full backup of the database via `mysqldump` into a `dump.sql` |
| [`import-db`](import-db/README.md) | Restores a full backup of the database via `mysql` / `mariadb` |
| [`export-web`](export-web/README.md) | Generates a static, dependency-free Website/HTML file that can be opened to visualize the database in regular web browsers |
| [`import-web`](import-web/README.md) | Restores data from the exported Website/HTML file |

## Requirements

- Python 3 (standard library only, no external packages to install)
- `mysql` / `mariadb` client tools (`mysql`, `mysqldump`) available on `PATH`
- A `MySQL` or `MariaDB` database server

## Getting started with the codebase

1. Create the database and load `schema.sql`
   ```bash
   mysql -u root -p -e "CREATE DATABASE frostpunk"
   mysql -u root -p frostpunk < schema.sql
   ```

2. Copy `.env.example` to `.env`
   ```bash
   cp .env.example .env
   ```

    And fill it with your environment details:

    | Name | Description | Default |
    |---|---|---|
    | `DB_HOST` | MySQL/MariaDB host | `127.0.0.1` |
    | `DB_PORT` | MySQL/MariaDB port | `3306` |
    | `DB_NAME` | Database name | `frostpunk` |
    | `DB_USER` | Database user | `frostpunk` |
    | `DB_PASSWORD` | Database password | `frostpunk` |

3. Load the environment variables before running any tool
   ```bash
   set -a; source .env; set +a
   ```

4. Populate the database
    - From latest database dump:
      1. Download the latest database dump from [Releases](../../releases)
      2. Load it with [`import-db`](import-db/README.md)

    - From latest generated webpage:
      1. Save the page as an HTML file
      2. Load it with [`import-web`](import-web/README.md)

    - From the Wiki directly (**advanced**):
      1. Open the [Scouting Wiki Page](https://frostpunk.fandom.com/wiki/Scouting)
      2. Manually insert new rows to the database using database management tool of your choice

## Database dump

Database dumps (scouting locations, discoveries, rewards) are published as assets on the [Releases](../../releases) page rather than committed to the git repository because that data carries a different [license](DATA_LICENSE.md) than the code (see below)

Grab the latest `dump.sql` from there and load it with [`import-db`](import-db/README.md) to skip manual data entry

## Contributing

Code changes, suggestions, and database dump contributions are all welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for how, and which license applies to what

## License & data attribution

The code and database schema in this repository are licensed under the [MIT License](LICENSE)

**The MIT License does not cover the actual database dump** — it contains content transcribed and adapted from the [Frostpunk Wiki](https://frostpunk.fandom.com/wiki/Scouting), which is [CC BY-NC-SA](DATA_LICENSE.md) licensed (attribution, non-commercial, share-alike)

The generated Website/HTML file contains credits to the wiki — please keep that credit if you intend to publish the generated page
