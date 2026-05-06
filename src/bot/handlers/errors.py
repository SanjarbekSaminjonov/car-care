from django.core.exceptions import ValidationError


def format_validation_error(exc: ValidationError) -> str:
    if hasattr(exc, "messages"):
        return " ".join(str(message) for message in exc.messages)
    return str(exc)
