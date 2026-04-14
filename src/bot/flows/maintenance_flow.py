from dataclasses import dataclass


@dataclass
class MaintenanceDraft:
    plate_number: str | None = None
    title: str | None = None
    odometer: int | None = None
    item_name: str | None = None
    item_amount: str | None = None


class MaintenanceFlowStateManager:
    def __init__(self) -> None:
        self._states: dict[int, str] = {}
        self._drafts: dict[int, MaintenanceDraft] = {}

    def start(self, chat_id: int) -> None:
        self._states[chat_id] = "awaiting_plate"
        self._drafts[chat_id] = MaintenanceDraft()

    def get_state(self, chat_id: int) -> str | None:
        return self._states.get(chat_id)

    def get_draft(self, chat_id: int) -> MaintenanceDraft | None:
        return self._drafts.get(chat_id)

    def clear(self, chat_id: int) -> None:
        self._states.pop(chat_id, None)
        self._drafts.pop(chat_id, None)

    def set_plate(self, chat_id: int, plate_number: str) -> None:
        self._drafts[chat_id].plate_number = plate_number
        self._states[chat_id] = "awaiting_title"

    def set_title(self, chat_id: int, title: str) -> None:
        self._drafts[chat_id].title = title
        self._states[chat_id] = "awaiting_odometer"

    def set_odometer(self, chat_id: int, odometer: int) -> None:
        self._drafts[chat_id].odometer = odometer
        self._states[chat_id] = "awaiting_item_name"

    def set_item_name(self, chat_id: int, item_name: str) -> None:
        self._drafts[chat_id].item_name = item_name
        self._states[chat_id] = "awaiting_item_amount"

    def set_item_amount(self, chat_id: int, item_amount: str) -> None:
        self._drafts[chat_id].item_amount = item_amount
        self._states[chat_id] = "awaiting_confirm"
