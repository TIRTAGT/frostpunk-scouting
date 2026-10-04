# Export: MySQL → static HTML page

Reads the database and generates a single self-contained page, `build/index.html`, with the data embedded as a JS object

The generated page has no external dependencies and works when opened directly from disk (`file://`) or from any static host.

Requires Python 3 (standard library only) and the `mysql`/`mariadb` client

## Usage

```bash
./export.py # database -> build/index.html
```

## Files

| File | Purpose |
|---|---|
| `export.py` | Queries the database and writes `build/index.html` |
| `template.html` | Page layout, styles and script; `/*__DATA__*/null` is replaced with the data |
| `build/` | Generated output |

## Notes

- Reward types are read from the `has_*` columns of `locations` and `rewards`, so new flag columns appear on the page without code changes. Add them to `REWARD_TYPES` in `export.py` for a proper display name, category (chip color) and position.
- The reward filter matches a location when a single choice yields all selected rewards; location-level flags (Trading Post) count for every choice.
- The page credits the Frostpunk Wiki (CC BY-NC-SA); keep the footer when publishing.
