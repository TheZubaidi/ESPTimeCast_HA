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

Recommended GitHub repository metadata for HACS validation:

- Description: `Home Assistant custom integration for ESPTimeCast LED clock devices`
- Topics: `home-assistant`, `hacs`, `hacs-integration`, `esptimecast`, `home-assistant-integration`

Brand assets used by HACS/Home Assistant are included at `custom_components/esptimecast/brand/icon.png` and `custom_components/esptimecast/brand/logo.png`.

## Manual Install

Copy `custom_components/esptimecast` into your Home Assistant `custom_components` directory and restart Home Assistant.

Then go to [**Settings > Devices & services**](https://my.home-assistant.io/redirect/integrations/) > **Add integration** > **ESPTimeCast** and enter the device IP address or hostname, such as `192.168.1.50` or `esptimecast.local`.

Home Assistant documentation:

- [Adding integrations](https://www.home-assistant.io/getting-started/integration/)
- [Automation actions](https://www.home-assistant.io/docs/automation/action/)

## Using the Integration

After setup, Home Assistant creates a device for each ESPTimeCast clock. Open the ESPTimeCast device page from **Settings > Devices & services** to see entities and controls.

Common controls:

- **Display brightness**: adjust LED brightness.
- **Clock duration** and **Weather duration**: control how long each mode is shown.
- **Time zone**, **Language**, **Weather city**, and **Weather country**: edit stored device settings.
- **Message to send**: type a message and send it directly to the clock.
- **Display**, **Flip display**, **Show day of the week**, **Animated seconds**, **Show date**, **12-hour clock**, **Use Fahrenheit**, **Show humidity**, and **Show weather description**: toggle common clock and weather settings.
- **Clear message**, **Next mode**, **Previous mode**, and **Restart**: run common ESPTimeCast actions.

Common status entities:

- Mode, current message, local time, Wi-Fi signal, temperature, humidity, firmware version, time sync, and display busy state.

ESPTimeCast firmware currently uses OpenWeather city/country settings. This integration exposes those fields instead of latitude/longitude because the current device API does not provide latitude/longitude config fields.

You do not need to edit Home Assistant YAML to add a device. YAML examples below are only for automations, scripts, and advanced users.

## Updates Through HACS

HACS creates update entities for tracked repositories, so users who install this integration through HACS can update it from Home Assistant when HACS detects a newer version.

There are two common ways to publish updates:

- **Default branch updates**: if you do not publish GitHub releases, HACS tracks the default branch and uses the latest commit as the available version. This is the easiest way for users to receive an update after you commit and push changes to GitHub.
- **GitHub release updates**: if you publish GitHub releases, HACS uses the latest published release tag as the available version. In that mode, users will not see every commit as an update; they will see updates when you publish a new GitHub release.

Recommended workflow for this repository:

1. Commit your changes.
2. Push to the default branch, usually `main`.
3. Let the included HACS validation workflow pass.
4. HACS users will see an update after HACS refreshes repository data. They may need to restart Home Assistant after updating an integration.

For stable public versions, publish GitHub releases such as `v0.1.1`, `v0.2.0`, and update `version` in `custom_components/esptimecast/manifest.json` to match. Use this release workflow only when you want users to update from releases instead of every default-branch commit.

Relevant HACS docs:

- [HACS update entities](https://www.hacs.xyz/docs/use/entities/update/)
- [HACS version behavior](https://www.hacs.xyz/docs/publish/start/#versions)

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

The integration intentionally exposes a compact set of practical entities: clock/weather settings, display controls, message controls, key status sensors, and a few useful action buttons. Advanced ESPTimeCast commands remain available through `esptimecast.action`.
