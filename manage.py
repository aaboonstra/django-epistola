#!/usr/bin/env python
import os
import sys

try:
    with open('epistola/site_settings.py') as f: pass
except IOError:
    import shutil
    shutil.copy('epistola/site_settings.py.template', 'epistola/site_settings.py')


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epistola.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
