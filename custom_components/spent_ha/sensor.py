from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_SHEKEL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SpentCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SpentCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = [
        SpentThisMonthSensor(coordinator, entry),
        SpentIncomeSensor(coordinator, entry),
        SpentCashFlowSensor(coordinator, entry),
        SpentUncategorizedSensor(coordinator, entry),
    ]

    # One sensor per category snapshot entry
    data = coordinator.data or {}
    for item in (data.get("categorySnapshot") or []):
        entities.append(SpentCategorySensor(coordinator, entry, item["name"]))

    async_add_entities(entities)


class _SpentBase(CoordinatorEntity[SpentCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: SpentCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Spent Finance",
            "manufacturer": "daveinc",
            "model": "Spent Finance Dashboard",
        }


class SpentThisMonthSensor(_SpentBase):
    _attr_icon = "mdi:currency-ils"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = CURRENCY_SHEKEL

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_this_month_spending"
        self._attr_name = "This Month Spending"

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        this_month = data.get("thisMonth") or {}
        return this_month.get("spent")

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        this_month = data.get("thisMonth") or {}
        return {
            "budget": this_month.get("budget"),
            "pace_phrase": this_month.get("pacePhrase"),
            "days_until_payday": this_month.get("daysUntilPayday"),
            "month_label": this_month.get("monthLabel"),
            "delta_vs_last_month_pct": this_month.get("deltaVsLastMonth"),
        }


class SpentIncomeSensor(_SpentBase):
    _attr_icon = "mdi:bank-transfer-in"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = CURRENCY_SHEKEL

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_this_month_income"
        self._attr_name = "This Month Income"

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        cash_flow = data.get("cashFlow") or {}
        return cash_flow.get("income")


class SpentCashFlowSensor(_SpentBase):
    _attr_icon = "mdi:cash-flow"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = CURRENCY_SHEKEL

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_cash_flow"
        self._attr_name = "Cash Flow"

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        cash_flow = data.get("cashFlow") or {}
        return cash_flow.get("net")


class SpentUncategorizedSensor(_SpentBase):
    _attr_icon = "mdi:tag-off"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_uncategorized"
        self._attr_name = "Uncategorized Transactions"

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        needs = data.get("needsAttention") or {}
        return needs.get("uncategorized", 0)


class SpentCategorySensor(_SpentBase):
    _attr_icon = "mdi:tag"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = CURRENCY_SHEKEL

    def __init__(self, coordinator, entry, category_name: str):
        super().__init__(coordinator, entry)
        slug = category_name.lower().replace(" ", "_")
        self._attr_unique_id = f"{entry.entry_id}_category_{slug}"
        self._attr_name = f"{category_name} Spending"
        self._category_name = category_name

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        for item in (data.get("categorySnapshot") or []):
            if item.get("name") == self._category_name:
                return item.get("spent")
        return None

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        for item in (data.get("categorySnapshot") or []):
            if item.get("name") == self._category_name:
                return {"budget": item.get("budget")}
        return {}
