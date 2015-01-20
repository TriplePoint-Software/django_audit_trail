from setuptools import setup

__version__ = "0.0.9"

setup(
    name='audit_trail',
    version=__version__,
    packages=['audit_trail', 'audit_trail.migrations', 'audit_trail.south_migrations'],
    url='https://github.com/AssuraGroup/audit_trail',
    license='',
    author_email='',
    description='',
    install_requires=["django == 1.7.3", "django-jsonfield==0.9.13"],
    tests_require=["django == 1.7.3", "django-jsonfield==0.9.13"],
    test_suite='runtests.runtests'

)
