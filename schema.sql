CREATE TABLE `scenarios` (
  `id` SMALLINT UNSIGNED NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `wiki_page` VARCHAR(150) NOT NULL,
  `notes` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `uq_scenarios_name` UNIQUE (`name`)
);

CREATE TABLE `locations` (
  `id` INT UNSIGNED NOT NULL,
  `scenario_id` SMALLINT UNSIGNED NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `is_home` TINYINT NOT NULL DEFAULT 0,
  `has_trading_post` TINYINT NOT NULL DEFAULT 0,
  `notes` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_locations_scenario` FOREIGN KEY (`scenario_id`) REFERENCES `scenarios` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `uq_locations_name` UNIQUE (`scenario_id`, `name`)
);

CREATE TABLE `location_discoveries` (
  `from_id` INT UNSIGNED NOT NULL,
  `to_id` INT UNSIGNED NOT NULL,
  `note` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`from_id`, `to_id`),
  INDEX `ix_discoveries_to` (`to_id` ASC),
  CONSTRAINT `fk_discoveries_to` FOREIGN KEY (`to_id`) REFERENCES `locations` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `fk_discoveries_from` FOREIGN KEY (`from_id`) REFERENCES `locations` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
);

-- A location may have multiple reward (OR) condition, one row per player choice
-- label: player choice (e.g. 'Leave intact'); NULL when the location has no choice
CREATE TABLE `rewards` (
  `id` INT UNSIGNED NOT NULL,
  `location_id` INT UNSIGNED NOT NULL,
  `label` VARCHAR(150) NULL DEFAULT NULL,
  -- Resources
  `has_wood` TINYINT NOT NULL DEFAULT 0,
  `has_coal` TINYINT NOT NULL DEFAULT 0,
  `has_steel` TINYINT NOT NULL DEFAULT 0,
  `has_raw_food` TINYINT NOT NULL DEFAULT 0,
  `has_food_rations` TINYINT NOT NULL DEFAULT 0,
  `has_steam_core` TINYINT NOT NULL DEFAULT 0,
  `has_steel_composites` TINYINT NOT NULL DEFAULT 0,
  `has_steam_exchangers` TINYINT NOT NULL DEFAULT 0,
  `has_structural_profiles` TINYINT NOT NULL DEFAULT 0,
  -- People
  `has_workers` TINYINT NOT NULL DEFAULT 0,
  `has_engineers` TINYINT NOT NULL DEFAULT 0,
  `has_children` TINYINT NOT NULL DEFAULT 0,
  -- Special
  `has_automaton` TINYINT NOT NULL DEFAULT 0,
  `has_outpost` TINYINT NOT NULL DEFAULT 0,
  `has_technology` TINYINT NOT NULL DEFAULT 0,
  `has_relics` TINYINT NOT NULL DEFAULT 0,
  `has_quest_objective` TINYINT NOT NULL DEFAULT 0,
  -- Risk
  `has_party_risk` TINYINT NOT NULL DEFAULT 0,
  `notes` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `uq_rewards_label` UNIQUE (`location_id`, `label`),
  CONSTRAINT `fk_rewards_location` FOREIGN KEY (`location_id`) REFERENCES `locations` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
);
