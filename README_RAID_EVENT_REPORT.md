# Raid Event Report (Map 52)

## Summary
This report describes the changes applied to support the RAID event "Siege of the Dark Rift" (map 52),
including the scripted time window, blocking the map when the event is closed, and mission adjustments.

## Key changes
- RAID event controlled by a fixed script window (`20:00` to `21:00`), with no database dependency.
- RAID event can be enabled/disabled via `RAID_EVENT_ENABLED` in the script (disables messages and access).
- Map 52 selection blocked when the event is closed, with a message showing the next opening time.
- Game start blocked if the room is set to map 52 while the event is closed.
- Map 52 missions automatically disabled when the RAID event is closed.
- Event status messages continue to be shown in the lobby, room, and at match start.
- Map 52 drops adjusted to rare (+4/+5) items across multiple bot_types with increased rates.

## Modified files
- `GameServer/Controllers/data/raid_event.py`
- `GameServer/Controllers/Room.py`
- `GameServer/Controllers/Missions.py`
- `GameServer/Controllers/data/planet.py`

## Related files (existing)
- `GameServer/Controllers/Lobby.py`
- `GameServer/Controllers/Game.py`

## Notes
- To change the raid schedule, adjust `RAID_OPEN_TIME` and `RAID_CLOSE_TIME` in
  `GameServer/Controllers/data/raid_event.py`.
