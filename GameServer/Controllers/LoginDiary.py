#!/usr/bin/env python3
__author__ = "Icseon"
__copyright__ = "Copyright (C) 2024"
__version__ = "1.0"

import datetime

from GameServer.Controllers.Character import add_item
from GameServer.Controllers.data.gifts import TYPE_ITEM
from GameServer.Controllers.data.login_rewards import LOGIN_REWARDS


def _get_reward_items(login_count):
    if not LOGIN_REWARDS:
        return []
    index = (login_count - 1) % len(LOGIN_REWARDS)
    return LOGIN_REWARDS[index]


def _fetch_game_item(_args, game_item_id):
    _args['mysql'].execute(
        """SELECT `id`, `name`, `duration`, `part_type` FROM `game_items` WHERE `id` = %s""", [
            game_item_id
        ])
    return _args['mysql'].fetchone()


def _fetch_login_state(_args, account_id):
    _args['mysql'].execute(
        """SELECT `id`, `login_count`, `month`, `year`, `last_login_date`
        FROM `login_diary` WHERE `account_id` = %s""", [
            account_id
        ])
    return _args['mysql'].fetchone()


def _upsert_login_state(_args, account_id, login_count, month, year, last_login_date):
    _args['mysql'].execute(
        """INSERT INTO `login_diary` (`account_id`, `login_count`, `month`, `year`, `last_login_date`)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            `login_count` = VALUES(`login_count`),
            `month` = VALUES(`month`),
            `year` = VALUES(`year`),
            `last_login_date` = VALUES(`last_login_date`)""", [
            account_id,
            login_count,
            month,
            year,
            last_login_date
        ])


def process_login(_args):
    today = datetime.datetime.utcnow().date()
    month = today.month
    year = today.year

    state = _fetch_login_state(_args, _args['client']['account_id'])
    login_count = 0
    last_login = None
    if state is not None:
        login_count = state['login_count']
        last_login = state['last_login_date']
        if state['month'] != month or state['year'] != year:
            login_count = 0

    if last_login == today:
        return login_count, []

    login_count += 1
    _upsert_login_state(_args, _args['client']['account_id'], login_count, month, year, today)

    rewards = []
    for game_item_id in _get_reward_items(login_count):
        item = _fetch_game_item(_args, game_item_id)
        if item is None:
            continue

        character_item_id = add_item(
            _args,
            {'id': item['id'], 'duration': item['duration'], 'part_type': item['part_type']},
            slot=0,
            inventory_insert=False
        )

        _args['mysql'].execute(
            """INSERT INTO `gifts` (`sender`, `receiver`, `date`, `message`, `type`, `item_1`)
            VALUES (NULL, %s, UTC_TIMESTAMP(), %s, %s, %s)""", [
                _args['client']['character']['id'],
                'Daily login reward',
                TYPE_ITEM,
                character_item_id
            ])

        rewards.append(item['name'])

    return login_count, rewards
