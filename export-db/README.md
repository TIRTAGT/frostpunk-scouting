# Export: MySQL → SQL dump

Wraps `mysqldump` (requires the `mysqldump` client) to back up the whole database (schema + data) to a single file

## Usage

```bash
./export.py                  # database -> build/dump.sql
./export.py /path/to/out.sql # explicit output path
```

## Files

| File | Purpose |
|---|---|
| `export.py` | Runs `mysqldump` and writes `build/dump.sql` |
| `build/` | Generated output |
