# Import: static HTML page → MySQL

Reads the embedded data object out of a generated `index.html` and loads it into the database

**This wipes and replaces all tables in the database**

## Usage

```bash
./import.py                     # ../export-web/build/index.html -> database
./import.py /path/to/index.html # explicit source file
```

## Files

| File | Purpose |
|---|---|
| `import.py` | Parses the embedded data and reloads the database |

## Notes

- The `has_*` flag columns are read from `information_schema` at run time, same as `export-web/export.py`, so new flag columns don't need code changes here either
- `location_discoveries` is rebuilt from each location's `leads_to` list only (its mirror, `found_from`, is the same edge seen from the other side, so using both would double-insert)
