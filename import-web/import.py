#!/usr/bin/env python3

"""
Import the export-web static page back into MySQL/MariaDB

This wipes and reloads the four tables; existing rows are discarded. Reward
rows get freshly assigned ids since export-web does not emit them (nothing
references rewards.id, so this is safe)
"""

import itertools
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

DIR = pathlib.Path(__file__).resolve().parent
DEFAULT_SOURCE = DIR.parent / "export-web" / "build" / "index.html"
DATA_RE = re.compile(r"const DATA = (.*?);\n")

# Child -> parent order, so FK references are always satisfiable even if checks were on.
TABLES = ("location_discoveries", "rewards", "locations", "scenarios")


class ImportFailure(Exception):
	pass

def check_env():
	missing = [k for k in ("DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD") if not os.environ.get(k)]
	if missing:
		raise ImportFailure(f"Missing connection settings: {', '.join(missing)}")

def mysql_client():
	client = shutil.which("mysql") or shutil.which("mariadb")
	if not client:
		raise ImportFailure("mysql/mariadb client not found")
	return client

def run_query(sql):
	"""Runs a query whose single column is a JSON document per row; returns the parsed rows."""
	cmd = [mysql_client(), "-h", os.environ["DB_HOST"], "-P", os.environ.get("DB_PORT", "3306"),
		"-u", os.environ["DB_USER"], "--default-character-set=utf8mb4",
		"--batch", "--raw", "--skip-column-names", os.environ["DB_NAME"], "-e", sql]
	env = dict(os.environ, MYSQL_PWD=os.environ["DB_PASSWORD"])
	res = subprocess.run(cmd, capture_output=True, text=True, env=env, check=False)
	if res.returncode != 0:
		raise ImportFailure(f"Query failed: {res.stderr.strip()}")
	return [json.loads(line) for line in res.stdout.splitlines() if line.strip()]

def run_script(sql):
	"""Executes a multi-statement SQL script via the client's stdin."""
	cmd = [mysql_client(), "-h", os.environ["DB_HOST"], "-P", os.environ.get("DB_PORT", "3306"),
		"-u", os.environ["DB_USER"], "--default-character-set=utf8mb4", os.environ["DB_NAME"]]
	env = dict(os.environ, MYSQL_PWD=os.environ["DB_PASSWORD"])
	res = subprocess.run(cmd, input=sql, capture_output=True, text=True, env=env, check=False)
	if res.returncode != 0:
		raise ImportFailure(f"Import failed: {res.stderr.strip()}")

def flag_columns(table):
	rows = run_query(
		"SELECT JSON_OBJECT('name', column_name) FROM information_schema.columns "
		f"WHERE table_schema = DATABASE() AND table_name = '{table}' AND column_name LIKE 'has\\\\_%' "
		"ORDER BY ordinal_position")
	return [r["name"] for r in rows]

def load_data(source):
	html = source.read_text(encoding="utf-8")
	m = DATA_RE.search(html)
	if not m:
		raise ImportFailure(f"Could not find embedded data object in {source}")
	return json.loads(m.group(1))

def sql_value(v):
	if v is None:
		return "NULL"
	if isinstance(v, bool):
		return "1" if v else "0"
	if isinstance(v, int):
		return str(v)
	return "'" + str(v).replace("\\", "\\\\").replace("'", "\\'") + "'"

def insert_stmt(table, columns, rows):
	if not rows:
		return ""
	cols_sql = ", ".join(f"`{c}`" for c in columns)
	values_sql = ", ".join("(" + ", ".join(sql_value(row[c]) for c in columns) + ")" for row in rows)
	return f"INSERT INTO `{table}` ({cols_sql}) VALUES {values_sql};\n"

def build_rows(data, loc_flags, reward_flags):
	scenarios, locations, rewards, discoveries = [], [], [], []
	reward_id = itertools.count(1)

	for scen in data["scenarios"]:
		scenarios.append({"id": scen["id"], "name": scen["name"], "wiki_page": scen["wiki_page"], "notes": scen["notes"]})
		for loc in scen["locations"]:
			row = {"id": loc["id"], "scenario_id": scen["id"], "name": loc["name"],
				"is_home": loc["is_home"], "notes": loc["notes"]}
			for col in loc_flags:
				row[col] = col[4:] in loc["types"]
			locations.append(row)

			for rew in loc["rewards"]:
				rrow = {"id": next(reward_id), "location_id": loc["id"], "label": rew["label"], "notes": rew["notes"]}
				for col in reward_flags:
					rrow[col] = col[4:] in rew["types"]
				rewards.append(rrow)

			for edge in loc["leads_to"]:
				discoveries.append({"from_id": loc["id"], "to_id": edge["id"], "note": edge["note"]})

	return scenarios, locations, rewards, discoveries

def run_import(source):
	loc_flags = flag_columns("locations")
	reward_flags = flag_columns("rewards")
	data = load_data(source)
	scenarios, locations, rewards, discoveries = build_rows(data, loc_flags, reward_flags)

	script = "SET FOREIGN_KEY_CHECKS=0;\n"
	for table in TABLES:
		script += f"TRUNCATE TABLE `{table}`;\n"
	script += insert_stmt("scenarios", ["id", "name", "wiki_page", "notes"], scenarios)
	script += insert_stmt("locations", ["id", "scenario_id", "name", "is_home", "notes"] + loc_flags, locations)
	script += insert_stmt("rewards", ["id", "location_id", "label", "notes"] + reward_flags, rewards)
	script += insert_stmt("location_discoveries", ["from_id", "to_id", "note"], discoveries)
	script += "SET FOREIGN_KEY_CHECKS=1;\n"

	run_script(script)
	return {"scenarios": len(scenarios), "locations": len(locations), "rewards": len(rewards),
		"discoveries": len(discoveries)}

if __name__ == "__main__":
	try:
		check_env()
		source = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SOURCE
		if not source.is_file():
			raise ImportFailure(f"Source file not found: {source}")
		counts = run_import(source)
	except ImportFailure as e:
		print(f"ERROR: {e}", file=sys.stderr)
		sys.exit(1)
	print(f"Imported from {source}:", ", ".join(f"{k}={v}" for k, v in counts.items()))
