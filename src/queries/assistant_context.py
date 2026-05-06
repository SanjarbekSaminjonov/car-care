from apps.cars.models import Car, MembershipStatus
from apps.maintenance.models import MaintenanceRecord


def get_car_context_for_user(*, user_id, max_records: int) -> dict:
    cars = list(
        Car.objects.filter(
            memberships__user_id=user_id,
            memberships__status=MembershipStatus.ACTIVE,
        )
        .distinct()
        .order_by("plate_number")
    )

    context_cars = []
    for car in cars:
        records = list(
            MaintenanceRecord.objects.filter(car=car)
            .order_by("-event_date", "-created_at")[:max_records]
        )
        context_cars.append(
            {
                "plate_number": car.plate_number,
                "brand": car.brand,
                "model": car.model,
                "year": car.year,
                "powertrain_type": car.powertrain_type,
                "current_odometer": car.current_odometer,
                "recent_maintenance": [
                    {
                        "event_date": record.event_date.isoformat(),
                        "odometer": record.odometer,
                        "title": record.title,
                        "description": record.description,
                        "total_amount": str(record.total_amount),
                        "status": record.status,
                    }
                    for record in records
                ],
            }
        )

    return {"cars": context_cars}
