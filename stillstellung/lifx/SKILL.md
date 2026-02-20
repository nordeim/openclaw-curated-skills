---
name: lifx
description: "Control LIFX smart lights via natural language. Toggle, set colors/brightness, activate scenes, create gradients on multi-zone devices."
homepage: https://github.com/Stillstellung/via-clara-claw
metadata:
  openclaw:
    emoji: "💡"
    requires:
      env: ["LIFX_TOKEN"]
---

# LIFX Light Control

Control LIFX smart lights via the LIFX HTTP API through natural language.

## References

- `lifx-api.sh` — Bash wrapper for all LIFX API calls
- `scene-status.py` — Scene matching and active detection
- `setup.sh` — Device discovery and skill configuration

## Configuration

Set your LIFX API token (get one at https://cloud.lifx.com/settings):

```bash
bash setup.sh <your-token>
```

This discovers your lights, groups, and scenes, then generates a personalized `SKILL.md` with your device context.

## Device Context

Location: **Maple Lane** — 24 lights, 11 rooms, 17 scenes, 1 multi-zone device(s).

### Rooms and Lights

| Room | Group ID | Lights |
|------|----------|--------|
| Basement | `486968148dc96708c4010c4d1ad6f3ed` | Basement C Front 1, Basement C Back 1, Basement C Back 2, Basement C Front 2 |
| Bedroom | `a68393c4103078091d0cb5cea4fd465b` | Bedroom Corner, Fan 1, Fan 3, Fan 2, Nightstand |
| Entrance | `900c5c64f69c820f2877df19dc5e3ca1` | Entrance Ceiling 2, Entrance Ceiling 1 |
| Garage | `2492b04f914e7980fb0bddf3555cd851` | Garage |
| Kitchen | `3a51cbe016ce411745f6fb5984cd1373` | Sink |
| Living Room | `db5356b4e4166c73c6a7da4b9742a5ce` | Silver Lamp, Back Lamp |
| Master Shower | `e8eaecec90582c1b390267bce3401a73` | Shower One, Shower Two |
| Office | `4033b4e975c7fba7ffbbb32de0e3da3c` | Office Corner |
| Porch | `55bf10fe4f5617b1d076cb4cab00446d` | Porch |
| Reading Room | `8e2fabffaa3b12212bb8a5c94a9f28eb` | Reading Room Bookshelf Lamp, Reading Room Floor Lamp, Reading Room Beam  ⚡multizone |
| Stairwell | `e6040214e4199c2c3e1366ec08741370` | Upstairs Hallway 2 , Upstairs Hallway 1 |

### Scenes

| Scene | UUID |
|-------|------|
| Basement Movie | `eace4433-ce88-46d3-a037-d97f97542c3f` |
| Basement Neutral | `715de535-2fd7-4470-9632-abda96029ce4` |
| Bedroom Bathroom Fade | `2ce39722-287c-49f9-bee0-6ee7ae8f616b` |
| Bedroom Comfy | `b5193a0c-d31f-44de-afd8-5075440b58f3` |
| Bedroom Neutral | `0cbc6f4e-8bc0-4e39-8372-c6e9237e874d` |
| Bedroom Sleepy | `e471b043-70c4-48ec-b2c0-6828ecc18289` |
| Hallways Neutral | `251d43fc-f3d1-4dc5-a218-7f0ca81d83ca` |
| House Asleep | `865a609b-5e5d-4cfd-b362-f6bc0ff29cfe` |
| House Stardust | `3e8c665f-adef-4042-8fd8-ab70f134ad2f` |
| Living Room Blue Night | `3a4b1b2c-cd69-41ae-8c43-cc54bc97bf08` |
| Living Room Lamps Daylight  | `f27ad3d6-2ee6-4d00-851c-6a716c9f6b0b` |
| Living Room Neutral | `801c2f77-1b2c-4cc3-9942-7a3b315fe63e` |
| Reading Room Game | `1c0d09d5-f550-4be3-b46a-01f30798b3eb` |
| Reading Room Oceanic | `4b1989fc-7001-4de8-a579-c485d09df780` |
| Reading Room RB | `c7abe95f-5489-4f7c-a7fb-3f9b9278cac6` |
| Reading Room White | `77d3c13d-bb28-409f-92e1-b97a2d3da7be` |
| Vibey Shower | `e20e70fe-b4d1-46fc-b565-30f5b24e586b` |

### Multi-zone Devices

- **Reading Room Beam** (`id:d073d5d0a7d9`) — supports zone-based gradients

## How to Control Lights

### Discover lights

```bash
bash lifx-api.sh discover
```

Shows all lights organized by room with power state, color, and brightness.

### Toggle lights on/off

```bash
bash lifx-api.sh toggle <selector>
```

Selectors:
- Individual light: `id:<light_id>`
- Group/room: `group_id:<group_id>`
- All lights: `all`

### Set light state (color, brightness, power)

```bash
bash lifx-api.sh state <selector> '{"power":"on","color":"blue","brightness":0.75,"duration":1.0}'
```

Color formats:
- Named: `red`, `blue`, `green`, `white`, `warm white`, `purple`, `orange`
- Hex: `#ff6b35`
- Kelvin: `kelvin:2700` (warm) to `kelvin:6500` (cool daylight)
- HSB: `hue:240 saturation:1.0`

**Always include `"power":"on"` and a brightness value when setting colors**, or lights with brightness 0 will stay invisible.

### Activate a scene

```bash
bash lifx-api.sh scene <scene_uuid>
```

### Toggle a room

```bash
bash lifx-api.sh group-toggle <group_id>
```

### Multi-zone gradients (Beam / Strip devices)

Multi-zone devices support individually addressable zones. Create gradients by setting different zone ranges:

```bash
bash lifx-api.sh state 'id:<light_id>|0-4' '{"power":"on","color":"purple","brightness":1.0,"duration":1.0}'
bash lifx-api.sh state 'id:<light_id>|5-9' '{"power":"on","color":"red","brightness":1.0,"duration":1.0}'
```

The pipe character in zone selectors is automatically URL-encoded by the script.

### Check scene status

```bash
python3 scene-status.py all    # Show all active scenes
python3 scene-status.py check <uuid>  # Check specific scene
```

### List current light states

```bash
bash lifx-api.sh list    # Full JSON
bash lifx-api.sh groups  # Summary by room
```

## Behavior Guidelines

- When user says a room name, match it to the group IDs in the device context above.
- Default brightness to 1.0 (100%) when setting colors unless user specifies otherwise.
- Default duration to 1.0 seconds for smooth transitions.
- For "turn off" commands, use `{"power":"off"}` — don't toggle (toggling is ambiguous).
- For "turn on" commands, use `{"power":"on","brightness":1.0}` to ensure visibility.
- When asked about what's on/what scene is active, use the scene-status tool or discover command.
- Be conversational about results: "Done, bedroom is now blue at 75%" not "API returned 207".
