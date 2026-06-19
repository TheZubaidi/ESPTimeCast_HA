# ESPTimeCast Home Assistant Integration

This custom integration lets [Home Assistant](https://www.home-assistant.io/) configure ESPTimeCast devices from the Integrations UI, poll device status, and send display messages without YAML.

## Affiliation and Support

This project is an unofficial Home Assistant integration. I am not affiliated with ESPTimeCast or its maintainers.

Please support the original ESPTimeCast project directly:

- ESPTimeCast project: https://github.com/mfactory-osaka/ESPTimeCast
- ESPTimeCast issues and firmware support: https://github.com/mfactory-osaka/ESPTimeCast/issues

Use this repository for Home Assistant integration issues only.

## HACS Install

1. Publish this repository to GitHub.
2. In Home Assistant, open **HACS > Integrations > three-dot menu > Custom repositories**.
3. Add your GitHub repository URL.
4. Select **Integration** as the category.
5. Install **ESPTimeCast** from HACS.
6. Restart Home Assistant.

HACS documentation:

- [Using the HACS dashboard](https://www.hacs.xyz/docs/use/repositories/dashboard/)
- [HACS integration repository requirements](https://www.hacs.xyz/docs/publish/integration/)

After restart, go to [**Settings > Devices & services**](https://my.home-assistant.io/redirect/integrations/) > **Add integration** > **ESPTimeCast** and enter the device IP address or hostname, such as `192.168.1.50` or `esptimecast.local`.

Before publishing, update `issue_tracker` in `custom_components/esptimecast/manifest.json` to your repository's GitHub Issues URL.

## Manual Install

Copy `custom_components/esptimecast` into your Home Assistant `custom_components` directory and restart Home Assistant.

Then go to [**Settings > Devices & services**](https://my.home-assistant.io/redirect/integrations/) > **Add integration** > **ESPTimeCast** and enter the device IP address or hostname, such as `192.168.1.50` or `esptimecast.local`.

Home Assistant documentation:

- [Adding integrations](https://www.home-assistant.io/getting-started/integration/)
- [Automation actions](https://www.home-assistant.io/docs/automation/action/)

## Using the Integration

After setup, Home Assistant creates a device for each ESPTimeCast clock. Open the ESPTimeCast device page from **Settings > Devices & services** to see entities and controls.

Common controls:

- **Brightness**: adjust display brightness from Home Assistant.
- **Display**: turn the LED display on or off.
- **Flip display**, **12-hour clock**, **Show date**, and **Show humidity**: toggle common clock settings.
- **Clear message**, **Next mode**, **Previous mode**, **Restart**, and timer buttons: run common ESPTimeCast actions.

Common status entities:

- Mode, current message, firmware version, board, Wi-Fi signal, local time, runtimes.
- Weather temperature, humidity, and description when configured on the device.
- Countdown, Nightscout, YouTube, and Instagram fields when those features are configured on the device.

You do not need to edit Home Assistant YAML to add a device. YAML examples below are only for automations, scripts, and advanced users.

## Services

Home Assistant exposes these as actions/services. Use them from **Developer Tools > Actions**, automations, scripts, or dashboard helpers.

Use `esptimecast.send_message` to show a temporary message:

```yaml
action: esptimecast.send_message
data:
  message: "DOOR OPEN"
  seconds: 15
```

Optional fields include:

- `device_id`: target a specific ESPTimeCast device when you have more than one.
- `seconds`: auto-clear after this many seconds.
- `scrolls`: number of scroll cycles.
- `speed`: scroll speed.
- `big_numbers`: use large numeric display mode when supported by the message.
- `interrupt`: allow the message to interrupt the current display.

Use `esptimecast.clear_message` to clear the temporary Home Assistant/API message.

Use `esptimecast.action` for any ESPTimeCast `/action` command:

```yaml
action: esptimecast.action
data:
  action: go_to_mode
  value: clock
```

If more than one ESPTimeCast device is configured, include `device_id` in action calls. `config_entry_id` is also supported as a fallback.

## Exposed Entities

The integration exposes sensors for firmware, board, mode, message, Wi-Fi signal, runtimes, local time, weather, countdown, Nightscout, SNS counters, time zone, and language. It also exposes binary sensors for sync/busy/countdown/Nightscout/dimming states, a brightness number, common setting switches, and action buttons.
