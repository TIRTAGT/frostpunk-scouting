#!/usr/bin/env python3

"""
Export the scouting MySQL/MariaDB database into JS object in a single static HTML page
"""

import datetime
import json
import os
import pathlib
import shutil
import subprocess
import sys

DIR = pathlib.Path(__file__).resolve().parent
TEMPLATE = DIR / "template.html"
OG_IMAGE = DIR / "og-image.png"
OUT = DIR / "build" / "index.html"
PLACEHOLDER = "/*__DATA__*/null"
SITE_URL_PLACEHOLDER = "__SITE_URL__"

# Display name and category per reward flag column. Every "has_*" column in the
# locations/rewards tables must be listed here.
REWARD_TYPES = {
	"has_wood": ("Wood", "resource"),
	"has_coal": ("Coal", "resource"),
	"has_steel": ("Steel", "resource"),
	"has_raw_food": ("Raw Food", "resource"),
	"has_food_rations": ("Food Rations", "resource"),
	"has_steam_core": ("Steam Core", "resource"),
	"has_steel_composites": ("Steel Composites", "resource"),
	"has_steam_exchangers": ("Steam Exchangers", "resource"),
	"has_structural_profiles": ("Structural Profiles", "resource"),
	"has_workers": ("Workers", "people"),
	"has_engineers": ("Engineers", "people"),
	"has_children": ("Children", "people"),
	"has_automaton": ("Automaton", "special"),
	"has_outpost": ("Outpost", "special"),
	"has_trading_post": ("Trading Post", "special"),
	"has_technology": ("Technology", "special"),
	"has_relics": ("Relics", "special"),
	"has_quest_objective": ("Quest Objective", "special"),
	"has_party_risk": ("Risk of Losing Party", "risk"),
}


class ExportError(Exception):
	pass

def check_env():
	missing = [k for k in ("DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD") if not os.environ.get(k)]
	if missing:
		raise ExportError(f"Missing connection settings: {', '.join(missing)}")

def run_query(sql):
	"""Runs a query whose single column is a JSON document per row; returns the parsed rows."""
	client = shutil.which("mysql") or shutil.which("mariadb")
	if not client:
		raise ExportError("mysql/mariadb client not found")
	cmd = [client, "-h", os.environ["DB_HOST"], "-P", os.environ.get("DB_PORT", "3306"),
		"-u", os.environ["DB_USER"], "--default-character-set=utf8mb4",
		"--batch", "--raw", "--skip-column-names", os.environ["DB_NAME"], "-e", sql]
	env = dict(os.environ, MYSQL_PWD=os.environ["DB_PASSWORD"])
	res = subprocess.run(cmd, capture_output=True, text=True, env=env, check=False)
	if res.returncode != 0:
		raise ExportError(f"Query failed: {res.stderr.strip()}")
	return [json.loads(line) for line in res.stdout.splitlines() if line.strip()]

def flag_columns(table):
	rows = run_query(
		"SELECT JSON_OBJECT('name', column_name) FROM information_schema.columns "
		f"WHERE table_schema = DATABASE() AND table_name = '{table}' AND column_name LIKE 'has\\\\_%' "
		"ORDER BY ordinal_position")
	return [r["name"] for r in rows]

def json_object(columns):
	return "JSON_OBJECT(" + ", ".join(f"'{c}', `{c}`" for c in columns) + ")"

def reward_type(column):
	name, category = REWARD_TYPES[column]
	return {"code": column[4:], "name": name, "category": category}

def export():
	loc_flags = flag_columns("locations")
	reward_flags = flag_columns("rewards")
	unknown = [c for c in loc_flags + reward_flags if c not in REWARD_TYPES]
	if unknown:
		raise ExportError(f"Unknown reward flag column(s), add them to REWARD_TYPES: {', '.join(unknown)}")

	scenarios = run_query("SELECT " + json_object(["id", "name", "wiki_page", "notes"]) + " FROM scenarios ORDER BY id")
	locations = run_query("SELECT " + json_object(["id", "scenario_id", "name", "is_home", "notes"] + loc_flags)
		+ " FROM locations ORDER BY id")
	rewards = run_query("SELECT " + json_object(["id", "location_id", "label", "notes"] + reward_flags)
		+ " FROM rewards ORDER BY id")
	discoveries = run_query("SELECT " + json_object(["from_id", "to_id", "note"])
		+ " FROM location_discoveries ORDER BY from_id, to_id")

	by_loc = {}
	for loc in locations:
		by_loc[loc["id"]] = {
			"id": loc["id"],
			"name": loc["name"],
			"is_home": bool(loc["is_home"]),
			"notes": loc["notes"],
			"types": [c[4:] for c in loc_flags if loc[c]],
			"rewards": [],
			"leads_to": [],
			"found_from": [],
		}

	for r in rewards:
		by_loc[r["location_id"]]["rewards"].append({
			"label": r["label"],
			"types": [c[4:] for c in reward_flags if r[c]],
			"notes": r["notes"],
		})

	for d in discoveries:
		by_loc[d["from_id"]]["leads_to"].append({"id": d["to_id"], "note": d["note"]})
		by_loc[d["to_id"]]["found_from"].append({"id": d["from_id"], "note": d["note"]})

	reward_type_order = list(REWARD_TYPES)
	scenarios_out = [dict(s, locations=[]) for s in scenarios]
	data = {
		"generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
		"reward_types": [reward_type(c) for c in sorted(loc_flags + reward_flags, key=reward_type_order.index)],
		"scenarios": scenarios_out,
	}
	scen_by_id = {s["id"]: s for s in scenarios_out}
	for loc in locations:
		scen_by_id[loc["scenario_id"]]["locations"].append(by_loc[loc["id"]])

	# "</" is escaped so data can never close the surrounding <script> tag.
	payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
	template = TEMPLATE.read_text(encoding="utf-8")
	if PLACEHOLDER not in template:
		raise ExportError(f"Placeholder {PLACEHOLDER!r} not found in {TEMPLATE.name}")

	site_url = os.environ.get("SITE_URL", "http://127.0.0.1").rstrip("/")

	OUT.parent.mkdir(exist_ok=True)
	html = template.replace(PLACEHOLDER, payload).replace(SITE_URL_PLACEHOLDER, site_url)
	OUT.write_text(html, encoding="utf-8")
	shutil.copyfile(OG_IMAGE, OUT.parent / OG_IMAGE.name)
	return {"scenarios": len(scenarios), "locations": len(locations), "rewards": len(rewards),
		"discoveries": len(discoveries)}

if __name__ == "__main__":
	try:
		check_env()
		counts = export()
	except ExportError as e:
		print(f"ERROR: {e}", file=sys.stderr)
		sys.exit(1)
	print(f"Generated {OUT.relative_to(DIR)}:", ", ".join(f"{k}={v}" for k, v in counts.items()))
