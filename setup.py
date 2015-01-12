from setuptools import setup

__version__ = "0.0.01"

DJANGO_REQUIREMENT = "Django >= 1.7.2"
setup(
    name='audit_trail',
    version=__version__,
    packages=['audit_trail', 'audit_trail.migrations', 'audit_trail.south_migrations'],
    url='https://github.com/AssuraGroup/audit_trail',
    license='',
    author='syabro',
    author_email='',
    description='',
    install_requires=[DJANGO_REQUIREMENT],
    tests_require=[DJANGO_REQUIREMENT],
    test_suite='runtests.runtests'

)
