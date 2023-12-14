import os
from django.core.management import call_command
import pytest

# Set up Django before the tests are collected
@pytest.fixture(scope='session')
def django_db_setup():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xnart.settings")
    call_command('makemigrations')
    call_command('migrate')
