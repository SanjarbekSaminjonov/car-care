def format_start_message() -> str:
    return (
        "Salom! CarCare botga xush kelibsiz.\n"
        "Mashinalaringizni boshqarish, servis va odometr ma'lumotlarini yuritishingiz mumkin."
    )


def format_help_message() -> str:
    return (
        "Yordam menyusi:\n"
        "• /start — botni boshlash\n"
        "• /app — CarCare Web App\n"
        "• /help — yordam\n"
        "• /cars — mashinalar ro'yxati\n"
        "• /addcar — mashina qo'shish\n"
        "• /addmaintenance — servis yozuvi qo'shish\n"
        "• /history [davlat raqami] — servis tarixi\n"
        "• /share [davlat raqami] [viewer|manager] — mashinani ulashish\n"
        "• /join [invite-kod] — mashinaga qo'shilish\n"
        "• /attachmedia [davlat raqami] — oxirgi servisga media biriktirish\n"
        "• /ask savol — AI assistant\n"
        "• /cancel — joriy flowni bekor qilish"
    )


def _format_money(value) -> str:
    return f"{value:,.0f}".replace(",", " ")


def format_maintenance_history(records) -> str:
    if not records:
        return "Servis tarixi topilmadi."

    lines = ["Servis tarixi:"]
    for index, record in enumerate(records, start=1):
        lines.append("")
        lines.append(
            f"{index}. {record.event_date:%Y-%m-%d} | {record.car.plate_number} | {record.odometer} km"
        )
        lines.append(f"   {record.title}")
        lines.append(f"   Summa: {_format_money(record.total_amount)}")

        line_items = list(record.line_items.all())
        if line_items:
            item_summary = "; ".join(
                f"{item.name} ({_format_money(item.total_price)})" for item in line_items[:3]
            )
            if len(line_items) > 3:
                item_summary = f"{item_summary}; +{len(line_items) - 3} item"
            lines.append(f"   Itemlar: {item_summary}")

        media_count = getattr(record, "media_count", None)
        if media_count:
            lines.append(f"   Media: {media_count} ta")

    return "\n".join(lines)
