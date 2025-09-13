import datetime
import json
import logging
import os
import re
import time
from enum import Enum
from pathlib import Path
import random
from typing import Dict, List, Optional

import psutil
from pypresence import Presence

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class CharacterClass(Enum):
    MERCENARY = "Mercenary"
    MONK = "Monk"
    RANGER = "Ranger"
    SORCERESS = "Sorceress"
    WARRIOR = "Warrior"
    WITCH = "Witch"
    HUNTRESS = "Huntress"

    def get_ascendencies(self) -> Optional[List["ClassAscendency"]]:
        return {
            CharacterClass.MERCENARY: [
                ClassAscendency.WITCHHUNTER,
                ClassAscendency.GEMLING_LEGIONNAIRE,
            ],
            CharacterClass.MONK: [
                ClassAscendency.ACOLYTE_OF_CHAYULA,
                ClassAscendency.INVOKER,
            ],
            CharacterClass.RANGER: [
                ClassAscendency.DEADEYE,
                ClassAscendency.PATHFINDER,
            ],
            CharacterClass.SORCERESS: [
                ClassAscendency.CHRONOMANCER,
                ClassAscendency.STORMWEAVER,
            ],
            CharacterClass.WARRIOR: [
                ClassAscendency.TITAN,
                ClassAscendency.WARBRINGER,
            ],
            CharacterClass.WITCH: [
                ClassAscendency.BLOOD_MAGE,
                ClassAscendency.INFERNALIST,
            ],
            CharacterClass.HUNTRESS: [
                ClassAscendency.RITUALIST,
                ClassAscendency.AMAZON,
            ],
        }.get(self)


class ClassAscendency(Enum):
    WITCHHUNTER = "Witchhunter"
    GEMLING_LEGIONNAIRE = "Gemling Legionnaire"
    ACOLYTE_OF_CHAYULA = "Acolyte of Chayula"
    INVOKER = "Invoker"
    DEADEYE = "Deadeye"
    PATHFINDER = "Pathfinder"
    CHRONOMANCER = "Chronomancer"
    STORMWEAVER = "Stormweaver"
    TITAN = "Titan"
    WARBRINGER = "Warbringer"
    BLOOD_MAGE = "Blood Mage"
    INFERNALIST = "Infernalist"
    RITUALIST = "Ritualist"
    AMAZON = "Amazon"
    SMITH_OF_KITAVA = "Smith of Kitava"
    LICH = "Lich"
    TACTICIAN = "Tactician"

    def get_class(self) -> CharacterClass:
        return {
            ClassAscendency.WITCHHUNTER: CharacterClass.MERCENARY,
            ClassAscendency.GEMLING_LEGIONNAIRE: CharacterClass.MERCENARY,
            ClassAscendency.TACTICIAN: CharacterClass.MERCENARY,
            ClassAscendency.ACOLYTE_OF_CHAYULA: CharacterClass.MONK,
            ClassAscendency.INVOKER: CharacterClass.MONK,
            ClassAscendency.DEADEYE: CharacterClass.RANGER,
            ClassAscendency.PATHFINDER: CharacterClass.RANGER,
            ClassAscendency.CHRONOMANCER: CharacterClass.SORCERESS,
            ClassAscendency.STORMWEAVER: CharacterClass.SORCERESS,
            ClassAscendency.TITAN: CharacterClass.WARRIOR,
            ClassAscendency.WARBRINGER: CharacterClass.WARRIOR,
            ClassAscendency.SMITH_OF_KITAVA: CharacterClass.WARRIOR,
            ClassAscendency.BLOOD_MAGE: CharacterClass.WITCH,
            ClassAscendency.INFERNALIST: CharacterClass.WITCH,
            ClassAscendency.LICH: CharacterClass.WITCH,
            ClassAscendency.RITUALIST: CharacterClass.HUNTRESS,
            ClassAscendency.AMAZON: CharacterClass.HUNTRESS,
        }[self]


def find_game_log():
    logging.info("Waiting for the game start..")
    while True:
        try:
            for process in psutil.process_iter(["name", "exe"]):
                if process.info.get("name") == "PathOfExileSteam.exe":
                    full_path = process.info.get("exe")
                    if full_path:
                        game_dir = os.path.dirname(full_path)
                        logging.info(f"Found game log at {game_dir}")
                        return os.path.join(game_dir, "logs", "Client.txt")
        except Exception as e:
            logging.error(f"Error accessing processes: {e}")
        time.sleep(3)


def get_poe2_start_time():
    for process in psutil.process_iter(["name", "create_time"]):
        if process.info.get("name") == "PathOfExileSteam.exe":
            return int(process.info["create_time"])
    return int(datetime.datetime.now().timestamp())

APP_START_TIME = get_poe2_start_time()


def random_status():
    statuses = [
        "Exploring ancient ruins",
        "Leveling up your skills",
        "Defeating hordes of enemies",
        "Looting rare artifacts",
        "Crossing dark portals",
        "Enhancing powerful gear",
        "Learning forbidden magic",
        "Tracking down the next boss",
        "Joining the fight in the league",
        "Preparing for the final encounter",
    ]
    return random.choice(statuses)


def load_locations():
    file_path = Path("locations.json")
    url = "https://raw.githubusercontent.com/ezbooz/Path-Of-Exile-2-RPC/refs/heads/main/locations.json"

    if file_path.exists():
        try:
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                logging.info("Loaded locations from local cache.")
                return data.get("areas", {})
        except Exception as e:
            logging.error(f"Error reading cached locations: {e}")
            return {}

    try:
        import urllib.request

        with urllib.request.urlopen(url) as response:
            data = json.load(response)
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info("Downloaded and cached locations.")
        return data.get("areas", {})
    except Exception as e:
        logging.error(f"Failed to fetch locations from the server: {e}")
        return {}


def determine_location(area_name: str, locations: Dict[str, str]) -> Optional[str]:
    normalized_area_name = area_name

    if area_name.startswith("Map"):
        normalized_area_name = area_name[3:].split("_")[0]

    if normalized_area_name in locations.values():
        return normalized_area_name
    else:
        for key, value in locations.items():
            if normalized_area_name == key or normalized_area_name == value:
                return value

    return normalized_area_name


def find_last_level_up(line: str, regex_level: re.Pattern) -> Optional[Dict[str, str]]:
    if match := regex_level.search(line):
        username, base_class, level = match.groups()
        base_class = base_class.strip()
        try:
            if base_class in ClassAscendency._value2member_map_:
                ascension_class = base_class
                base_class = ClassAscendency(base_class).get_class().value
            else:
                ascension_class = "Unknown"
        except Exception:
            ascension_class = "Unknown"
        return {
            "username": username,
            "ascension_class": ascension_class,
            "base_class": base_class,
            "level": level,
        }
    return None


def get_last_level_up(
    log_file_path: Path, regex_level: re.Pattern
) -> Optional[Dict[str, str]]:
    try:
        with log_file_path.open("r", encoding="utf-8") as log_file:
            lines = log_file.readlines()
            for line in reversed(lines):
                if match := regex_level.search(line):
                    return find_last_level_up(line, regex_level)
    except Exception:
        pass
    return None


def find_instance(
    line: str, regex_instance: re.Pattern, locations: Dict[str, str]
) -> Optional[Dict[str, str]]:
    if match := regex_instance.search(line):
        level, area_name, seed = match.groups()
        location_name = determine_location(area_name, locations)
        return {
            "location_name": location_name or area_name,
            "location_level": level,
        }
    return None

def find_afk(line: str, regex_afk: re.Pattern) -> Optional[bool]:
    if match := regex_afk.search(line):
        state = match.group(1).upper()
        return state == "ON"
    return None


def get_details(level_info):
    return (
        f"{level_info['username']} - {level_info['base_class']}"
        + (
            f" {level_info['ascension_class']}"
            if level_info["ascension_class"] != "Unknown"
            else ""
        )
        + f" - Level {level_info['level']}"
    )

def rpc_connect():
    retries = 0
    while retries < 5:
        try:
            rpc = Presence("1315800372207419504")
            rpc.connect()
            logging.info("Connected to Discord RPC.")
            return rpc
        except Exception as e:
            retries += 1
            logging.error(f"Retrying RPC connection, attempt {retries}...")
            time.sleep(2**retries)
            logging.warning(f"Error connecting to Discord RPC: {e}")
    logging.error(
        f"Failed to connect to Discord RPC after multiple retries.  Please ensure Discord is running and the application is authorized."
    )
    return None


def update_rpc(level_info, instance_info=None, status=None, current_status=None):
    try:
        if current_status and current_status.get("afk_status", False):
            now = time.time()
            if now - current_status.get("last_switch_time", 0) > 3:
                current_status["afk_toggle"] = not current_status.get("afk_toggle", False)
                current_status["last_switch_time"] = now

            if current_status.get("afk_toggle", False):
                status = "💤 AFK mode enabled"
            else:
                if instance_info:
                    status = f"In: {instance_info['location_name']} (Lvl {instance_info['location_level']})"
                else:
                    status = random_status()
        else:
            if instance_info:
                status = f"In: {instance_info['location_name']} (Lvl {instance_info['location_level']})"
            elif status is None:
                status = random_status()

        rpc.update(
            details=get_details(level_info),
            state=status,
            start=APP_START_TIME,
            small_image=level_info["ascension_class"].lower().replace(" ", "_"),
        )
    except Exception as e:
        logging.error(f"Failed to update RPC: {e}")


regex_level = re.compile(r": (\w+) \(([\w\s]+)\) is now level (\d+)")
regex_instance = re.compile(r'Generating level (\d+) area "([^"]+)" with seed (\d+)')
regex_afk = re.compile(r": AFK mode is now (\w+)")

def monitor_log():
    game_path = find_game_log()

    log_file_path = Path(game_path)
    locations = load_locations()

    last_level_info = get_last_level_up(log_file_path, regex_level)
    if last_level_info:
        rpc.update(
            details=get_details(last_level_info),
            state=random_status(),
            start=APP_START_TIME,
            small_image=last_level_info["ascension_class"].lower(),
        )

    with log_file_path.open("r", encoding="utf-8") as log_file:
        log_file.seek(0, 2)

        current_status = {"level_info": last_level_info, "instance_info": None, "afk_status": False, "afk_toggle": False, "last_switch_time": 0}

        while True:
            new_lines = log_file.readlines()
            updated = False

            for line in new_lines:
                level_info = find_last_level_up(line, regex_level)
                if level_info and (level_info != current_status.get("level_info")):
                    current_status["level_info"] = level_info
                    updated = True

                instance_info = find_instance(line, regex_instance, locations)
                if instance_info and (instance_info != current_status.get("instance_info")):
                    current_status["instance_info"] = instance_info
                    updated = True

                afk_state = find_afk(line, regex_afk)
                if afk_state is not None:
                    current_status["afk_status"] = afk_state
                    updated = True

            update_rpc(
                current_status["level_info"],
                current_status.get("instance_info"),
                current_status=current_status
            )

            time.sleep(5)


if __name__ == "__main__":
    rpc = rpc_connect()
    monitor_log()