#!/usr/bin/env python3

"""
Load a SQL dump produced by ../export-db back into MySQL/MariaDB
"""

import os
import pathlib
import shutil
import subprocess
import sys

DIR = pathlib.Path(__file__).resolve().parent
DEFAULT_SOURCE = DIR.parent / "export-db" / "build" / "dump.sql"


class ImportFailure(Exception):
	pass

def check_env():
	missing = [k for k in ("DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD") if not os.environ.get(k)]
	if missing:
		raise ImportFailure(f"Missing connection settings: {', '.join(missing)}")

def load(source):
	client = shutil.which("mysql") or shutil.which("mariadb")
	if not client:
		raise ImportFailure("mysql/mariadb client not found")
	cmd = [client, "-h", os.environ["DB_HOST"], "-P", os.environ.get("DB_PORT", "3306"),
		"-u", os.environ["DB_USER"], "--default-character-set=utf8mb4", os.environ["DB_NAME"]]
	env = dict(os.environ, MYSQL_PWD=os.environ["DB_PASSWORD"])
	with source.open("r", encoding="utf-8") as f:
		res = subprocess.run(cmd, stdin=f, capture_output=True, text=True, env=env, check=False)
	if res.returncode != 0:
		raise ImportFailure(f"Import failed: {res.stderr.strip()}")

if __name__ == "__main__":
	try:
		check_env()
		source = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SOURCE
		if not source.is_file():
			raise ImportFailure(f"Source file not found: {source}")
		load(source)
	except ImportFailure as e:
		print(f"ERROR: {e}", file=sys.stderr)
		sys.exit(1)
	print(f"Loaded {source} into {os.environ['DB_NAME']}")
