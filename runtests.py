#!/usr/bin/env python

import os
import sys

from django.conf import settings
import django


DEFAULT_SETTINGS = dict(
    INSTALLED_APPS=(
        'django.contrib.contenttypes',
        'django.contrib.auth',

        'audit_trail',
        '_test_project.test_app',
    ),
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3"
        }
    },
    SILENCED_SYSTEM_CHECKS=["1_7.W001"],
)


def runtests():
    if not settings.configured:
        settings.configure(**DEFAULT_SETTINGS)

    # Compatibility with Django 1.7's stricter initialization
    if hasattr(django, 'setup'):
        django.setup()

    parent = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, parent)

    try:
        from django.test.runner import DiscoverRunner

        runner_class = DiscoverRunner
        test_args = ['_test_project.test_app']
    except ImportError:
        # Disabled
        # - pylint: E0611 / No name 'simple' in module 'django.test'
        # - pylint: F0401 / Unable to import 'django.test.simple'
        # pylint: disable= F0401, E0611
        from django.test.simple import DjangoTestSuiteRunner

        runner_class = DjangoTestSuiteRunner
        test_args = ['tests']

    failures = runner_class(verbosity=1, interactive=True, failfast=False).run_tests(test_args)
    sys.exit(failures)


if __name__ == '__main__':
    runtests()
