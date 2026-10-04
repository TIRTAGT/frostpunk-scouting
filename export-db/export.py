#!/usr/bin/env python3

"""
Dump the scouting MySQL/MariaDB database (schema + data) to a single SQL file via mysqldump
"""

import os
import pathlib
import shutil
import subprocess
import sys

DIR = pathlib.Path(__file__).resolve().parent
DEFAULT_OUT = DIR / "build" / "dump.sql"


class ExportError(Exception):
	pass

def check_env():
	missing = [k for k in ("DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD") if not os.environ.get(k)]
	if missing:
		raise ExportError(f"Missing connection settings: {', '.join(missing)}")

def dump(out):
	client = shutil.which("mysqldump")
	if not client:
		raise ExportError("mysqldump client not found")
	cmd = [client, "-h", os.environ["DB_HOST"], "-P", os.environ.get("DB_PORT", "3306"),
		"-u", os.environ["DB_USER"], "--default-character-set=utf8mb4",
		"--single-transaction", "--routines", "--triggers", os.environ["DB_NAME"]]
	env = dict(os.environ, MYSQL_PWD=os.environ["DB_PASSWORD"])
	out.parent.mkdir(parents=True, exist_ok=True)
	with out.open("w", encoding="utf-8") as f:
		res = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True, env=env, check=False)
	if res.returncode != 0:
		raise ExportError(f"mysqldump failed: {res.stderr.strip()}")

if __name__ == "__main__":
	try:
		check_env()
		out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
		dump(out)
	except ExportError as e:
		print(f"ERROR: {e}", file=sys.stderr)
		sys.exit(1)
	print(f"Dumped {os.environ['DB_NAME']} to {out}")
