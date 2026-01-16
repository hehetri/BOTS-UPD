import datetime
import math

import MySQL.Interface as MySQL

RAID_EVENT_MAP_ID = 52
RAID_EVENT_NAME = 'O Cerco da Fenda Sombria'


def _fetch_next_raid_event(_args, now, map_id):
    mysql_connection = None
    mysql_cursor = _args.get('mysql')
    if mysql_cursor is None:
        mysql_connection = MySQL.get_connection()
        mysql_cursor = mysql_connection.cursor(dictionary=True)

    mysql_cursor.execute(
        """SELECT `map_id`, `start_time`, `end_time`
        FROM `raid_event`
        WHERE `map_id` = %s AND `end_time` >= %s
        ORDER BY `start_time` ASC
        LIMIT 1""", [
            map_id,
            now
        ])
    row = mysql_cursor.fetchone()
    if mysql_connection:
        mysql_connection.close()
    return row


def build_raid_event_message(_args, now=None, map_id=RAID_EVENT_MAP_ID):
    current_time = now or datetime.datetime.now()
    raid_event = _fetch_next_raid_event(_args, current_time, map_id)
    if not raid_event:
        return None

    start_time = raid_event.get('start_time')
    end_time = raid_event.get('end_time')
    if not start_time or not end_time:
        return None

    if current_time < start_time:
        minutes = max(0, math.ceil((start_time - current_time).total_seconds() / 60))
        return '[Raid] A raid "{0}" abre em {1} minuto(s).'.format(RAID_EVENT_NAME, minutes), 3

    if start_time <= current_time <= end_time:
        remaining = max(0, math.ceil((end_time - current_time).total_seconds() / 60))
        if remaining <= 10:
            message = '[Raid] A raid "{0}" fecha em {1} minuto(s)!'.format(RAID_EVENT_NAME, remaining)
        else:
            message = '[Raid] A raid "{0}" está aberta! Encerramento em {1} minuto(s).'.format(
                RAID_EVENT_NAME,
                remaining
            )
        return message, 3

    return None
