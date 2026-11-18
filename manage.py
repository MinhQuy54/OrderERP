#!/usr/bin/env python
"""Tiện ích dòng lệnh Django cho các tác vụ quản trị."""
import os
import sys


def main():
    """Chạy các tác vụ quản trị."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aurascent_erp.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Không thể import Django. Hãy đảm bảo Django đã được cài đặt "
            "và môi trường ảo đang được kích hoạt."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

