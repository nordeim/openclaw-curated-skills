---
name: flights
description: CLI tool to control Tuya v3.3 light bulbs in your local network.
metadata: {"clawdbot":{"emoji":"💡","requires":{"bins":["flights"]},"install":[{"id":"brew","kind":"brew","formula":"BrewTheFox/flights/flights","bins":["flights"], "args": ["--with-binary"], "label":"Install flights (brew)"}]}, "additional": {"formula_repo":"https://github.com/BrewTheFox/homebrew-flights", "source_repo":"https://github.com/BrewTheFox/flights", "architecture":"for other architectures that are not Linux X86_64 remove all args to build from source"}}
---
**flights (fox-lights cli)**

flights is a CLI tool to control *Tuya v3.3* light bulbs. Designed to *store multiple light bulbs in the same place*.

*device information is stored in this file:*  `~/.config/flights/bulbs.json`.

Each device contains the following fields: 
```json
{
    name (set by the user).
    key (Tuya local key. The length of this field MUST always be equal 16) (Changes when the bulb unlinks from the Tuya Account).
    id (Tuya bulb ID. The length of this field MUST always be equal 22).
    ip (The local IP address of the bulb).
}

```

## Configuration

to configure flights follow this steps:

- Check if flights is installed by executing `flights --help`.
    - If it is installed you will be greeted with the help menu. Hint: the returned text starts with `Usage: flights <COMMAND>`

- Check if there are lights already available with `flights list`.
    - If there are lights configured already you may skip the following steps.
    - If the list is empty (the only output is "Name, ID") you will have to add a device. 

- To add a lightbulb you can use the command `flights add --name {device name} --key {escaped key} --id {device id} --ip {device ip address}`

## Commands

| Command | Information | Arguments (All of them are mandatory) |
|---|---|---|
| flights add | adds a light bulb  | --name (name for the bulb) --key (Tuya local key. len = 16) --id (Tuya device ID. len = 22) --ip (local ip address of the bulb). |
| flights remove | removes a light bulb | --name (name of the bulb that is being removed) |
| flights list | lists all of the connected bulbs | None |
| flights on | turn on a light bulb | --name (name of the bulb to turn on) |
| flights off | turn off a light bulb | --name (name of the bulb to turn off) |
| flights color | change the color of a light bulb | --name (name of the bulb) --hex-color (six digit hex color code that the bulb is going to change to) |
| flights white | sets the color of a light bulb to white | -name (name of the bulb) |
| flights brightness | sets the brightness of a light bulb to a desired amount | --name (name of the bulb) --percent (a number ranging between 1-100 containing the desired percent (without the % sign))  |
| flights status | retrieves the status of a light bulb | --name (name of the bulb to retrieve) |
## Additional

- You can restore the configuration by deleting the file in `~/.config/flights`.
- You can fetch the status of a bulb to change its params later.
