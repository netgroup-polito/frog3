#!/usr/bin/env python
import os
import sys
import logging
from webContent.constants import LOG_LEVEL


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")

    log_format = '[%(asctime)s] %(levelname)s %(message)s - %(filename)s'

    logging.basicConfig(level=LOG_LEVEL, format=log_format, datefmt='%m/%d/%Y %I:%M:%S %p')
    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.WARNING)


    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
