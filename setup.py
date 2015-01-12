from distutils.core import setup

__version__ = "0.0.01"

setup(
    name='audit_trail',
    version=__version__,
    packages=['audit_trail', 'audit_trail.migrations'],
    url='https://github.com/AssuraGroup/audit_trail',
    license='',
    author='syabro',
    author_email='',
    description='',
    install_requires=[
        "Django >= 1.7.2",
    ],
)
