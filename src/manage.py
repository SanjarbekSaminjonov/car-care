#!/usr/bin/env python3
import os
import sys
from pathlib import Path


def prepare_python_path() -> None:
    src_dir = str(Path(__file__).resolve().parent)
    if src_dir in sys.path:
        sys.path.remove(src_dir)
        sys.path.append(src_dir)


def main() -> None:
    prepare_python_path()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django import qilinmadi. Avval dependency'larni o'rnating."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
