import logging

from homeassistant.components.sensor import ( SensorEntityDescription, RestoreSensor )
from .base import ( StellantisBaseSensor, StellantisRestoreSensor )

from .const import (
    DOMAIN,
    SENSORS_DEFAULT
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities) -> None:
    stellantis = hass.data[DOMAIN][entry.entry_id]
    entities = []

    vehicles = await stellantis.get_user_vehicles()

    for vehicle in vehicles:
        coordinator = await stellantis.async_get_coordinator(vehicle)

        for key in SENSORS_DEFAULT:
            default_value = SENSORS_DEFAULT.get(key, {})
            if default_value.get("data_map", None):
                description = SensorEntityDescription(
                    name = key,
                    key = key,
                    translation_key = key,
                    icon = default_value.get("icon", None),
                    unit_of_measurement = default_value.get("unit_of_measurement", None),
                    device_class = default_value.get("device_class", None)
                )
                entities.extend([StellantisBaseSensor(coordinator, description, default_value.get("data_map", None))])

        description = SensorEntityDescription(
            name = "command_status",
            key = "command_status",
            translation_key = "command_status",
            icon = "mdi:format-list-bulleted-type"
        )
        entities.extend([StellantisCommandStatusSensor(coordinator, description)])

#         await coordinator.async_request_refresh()

    async_add_entities(entities)


class StellantisCommandStatusSensor(StellantisRestoreSensor):
    def coordinator_update(self):
        actions_status = self._coordinator._actions_status
        if not actions_status:
            return

        attributes = {}
        for index, status in enumerate(actions_status):
            if index == 0:
                self._attr_native_value = status
            else:
                attributes[f"previus_{index}"] = status

        self._attr_extra_state_attributes = attributes