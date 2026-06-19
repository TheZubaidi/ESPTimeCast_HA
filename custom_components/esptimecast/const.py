"""Constants for the ESPTimeCast integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "esptimecast"
PLATFORMS = ["sensor", "binary_sensor", "number", "switch", "button", "text"]

CONF_HOST = "host"
CONF_PORT = "port"

DEFAULT_PORT = 80
DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)
REQUEST_TIMEOUT = 10

SERVICE_SEND_MESSAGE = "send_message"
SERVICE_CLEAR_MESSAGE = "clear_message"
SERVICE_ACTION = "action"

ATTR_CONFIG_ENTRY_ID = "config_entry_id"
ATTR_DEVICE_ID = "device_id"
ATTR_MESSAGE = "message"
ATTR_SECONDS = "seconds"
ATTR_SCROLLS = "scrolls"
ATTR_SPEED = "speed"
ATTR_BIG_NUMBERS = "big_numbers"
ATTR_INTERRUPT = "interrupt"
ATTR_ACTION = "action"
ATTR_VALUE = "value"
