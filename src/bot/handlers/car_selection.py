from apps.cars.models import Car


def format_manageable_car_choices(cars: list[Car], *, action_label: str) -> str:
    lines = [f"{action_label} uchun mashinani tanlang:"]
    for index, car in enumerate(cars, start=1):
        odometer = (
            f" | {car.current_odometer} km"
            if car.current_odometer is not None
            else ""
        )
        lines.append(
            f"{index}. {car.plate_number} | {car.brand} {car.model} ({car.year}){odometer}"
        )
    lines.append("Raqam yoki davlat raqamini yuboring.")
    return "\n".join(lines)


def resolve_selected_car(cars: list[Car], text: str) -> Car | None:
    normalized_text = text.strip()
    if normalized_text.isdigit():
        index = int(normalized_text)
        if 1 <= index <= len(cars):
            return cars[index - 1]

    normalized_plate = Car.normalize_plate(normalized_text)
    for car in cars:
        if car.normalized_plate_number == normalized_plate:
            return car
    return None
