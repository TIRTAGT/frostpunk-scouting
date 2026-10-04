# Import: SQL dump → MySQL

Loads a `mysqldump` file (as produced by `../export-db`) back into the
database using `mysql` / `mariadb` client (requires the client to be installed)

**This wipes and replaces all tables in the database**

## Usage

```bash
./import.py                   # ../export-db/build/dump.sql -> database
./import.py /path/to/dump.sql # explicit source file
```

## Files

| File | Purpose |
|---|---|
| `import.py` | Streams the dump file into the `mysql` client |
