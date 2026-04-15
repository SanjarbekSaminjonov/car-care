from dataclasses import dataclass


@dataclass
class CarDraft:
    plate_number: str | None = None
    brand: str | None = None
    model: str | None = None


class CarFlowStateManager:
    """Temporary in-memory state store for car flow (DB persistence in TASK-017)."""

    def __init__(self) -> None:
        self._states: dict[int, str] = {}
        self._drafts: dict[int, CarDraft] = {}

    def start(self, chat_id: int) -> None:
        self._states[chat_id] = "awaiting_plate"
        self._drafts[chat_id] = CarDraft()

    def get_state(self, chat_id: int) -> str | None:
        return self._states.get(chat_id)

    def get_draft(self, chat_id: int) -> CarDraft | None:
        return self._drafts.get(chat_id)

    def set_plate(self, chat_id: int, plate_number: str) -> None:
        draft = self._drafts[chat_id]
        draft.plate_number = plate_number
        self._states[chat_id] = "awaiting_brand"

    def set_brand(self, chat_id: int, brand: str) -> None:
        draft = self._drafts[chat_id]
        draft.brand = brand
        self._states[chat_id] = "awaiting_model"

    def set_model(self, chat_id: int, model: str) -> None:
        draft = self._drafts[chat_id]
        draft.model = model
        self._states[chat_id] = "awaiting_year"

    def clear(self, chat_id: int) -> None:
        self._states.pop(chat_id, None)
        self._drafts.pop(chat_id, None)
