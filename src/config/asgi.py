import os
import sys
from pathlib import Path

from django.core.asgi import get_asgi_application


def prepare_python_path() -> None:
    src_dir = str(Path(__file__).resolve().parents[1])
    if src_dir in sys.path:
        sys.path.remove(src_dir)
        sys.path.append(src_dir)


prepare_python_path()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

application = get_asgi_application()
