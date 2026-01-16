#!/usr/bin/env python3
__author__ = "Icseon"
__copyright__ = "Copyright (C) 2024"
__version__ = "1.0"

from GameServer.Controllers.data.planet import PLANET_MISSIONS
from GameServer.Controllers.data.raid_event import is_raid_event_open, RAID_EVENT_MAP_ID


def get_missions_for_map(map_id):
    if map_id == RAID_EVENT_MAP_ID and not is_raid_event_open():
        return []
    return PLANET_MISSIONS.get(map_id, [])


def get_progress(_args, character_id, map_id, mission_key):
    _args['mysql'].execute(
        """SELECT `progress`, `required`, `completed` FROM `character_missions`
        WHERE `character_id` = %s AND `map_id` = %s AND `mission_key` = %s""", [
            character_id,
            map_id,
            mission_key
        ])
    return _args['mysql'].fetchone()


def upsert_progress(_args, character_id, map_id, mission, increment=0):
    existing = get_progress(_args, character_id, map_id, mission['key'])
    progress = increment
    completed = 0

    if existing is not None:
        progress = existing['progress'] + increment
        completed = existing['completed']

    if progress > mission['required']:
        progress = mission['required']

    if existing is None:
        _args['mysql'].execute(
            """INSERT INTO `character_missions`
            (`character_id`, `map_id`, `mission_key`, `mission_type`, `target_id`,
             `progress`, `required`, `reward_exp`, `completed`)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", [
                character_id,
                map_id,
                mission['key'],
                mission['type'],
                mission.get('target_id'),
                progress,
                mission['required'],
                mission['reward_exp'],
                completed
            ])
    else:
        _args['mysql'].execute(
            """UPDATE `character_missions`
            SET `progress` = %s, `required` = %s, `reward_exp` = %s
            WHERE `character_id` = %s AND `map_id` = %s AND `mission_key` = %s""", [
                progress,
                mission['required'],
                mission['reward_exp'],
                character_id,
                map_id,
                mission['key']
            ])

    return progress, completed


def complete_mission(_args, character_id, map_id, mission_key):
    _args['mysql'].execute(
        """UPDATE `character_missions`
        SET `completed` = 1, `completed_at` = UTC_TIMESTAMP()
        WHERE `character_id` = %s AND `map_id` = %s AND `mission_key` = %s AND `completed` = 0""", [
            character_id,
            map_id,
            mission_key
        ])
    return _args['mysql'].rowcount > 0


def process_planet_missions(_args, character, map_id, won, boss_killed, monster_kills):
    if not won:
        return 0

    reward_exp_total = 0
    missions = get_missions_for_map(map_id)
    for mission in missions:
        increment = 0
        if mission['type'] == 'complete':
            increment = 1
        elif mission['type'] == 'boss' and mission.get('target_id') is not None and boss_killed:
            increment = 1
        elif mission['type'] == 'kills' and monster_kills > 0:
            increment = monster_kills

        if increment == 0:
            continue

        progress, completed = upsert_progress(
            _args,
            character['id'],
            map_id,
            mission,
            increment=increment
        )

        if completed == 0 and progress >= mission['required']:
            if complete_mission(_args, character['id'], map_id, mission['key']):
                reward_exp_total += mission['reward_exp']

    if reward_exp_total > 0:
        character['experience'] = character['experience'] + reward_exp_total
        _args['mysql'].execute(
            """UPDATE `characters` SET `experience` = (`experience` + %s) WHERE `id` = %s""", [
                reward_exp_total,
                character['id']
            ])

    return reward_exp_total


def format_missions_for_chat(_args, character_id, map_id):
    missions = get_missions_for_map(map_id)
    lines = []
    for mission in missions:
        progress_row = get_progress(_args, character_id, map_id, mission['key'])
        progress = progress_row['progress'] if progress_row else 0
        required = mission['required']
        completed = bool(progress_row and progress_row['completed'])
        status = "COMPLETED" if completed else "IN PROGRESS"
        reward_text = "REWARD RECEIVED: +{0} EXP".format(mission['reward_exp']) if completed \
            else "REWARD: +{0} EXP".format(mission['reward_exp'])
        lines.append({
            "message": "[QUEST] {0} ({1}/{2}) - {3} - {4}".format(
                mission['name'],
                progress,
                required,
                status,
                reward_text
            ),
            "completed": completed
        })
    return lines
