#!/usr/bin/env python
# Encoding: utf-8

import re
import subprocess

__author__ = 'syabro'


def get_last_version_from_tags():
    versions = subprocess.check_output(["git", "tag"])
    versions = versions.split('\n')
    version_regex = re.compile('(\d+)\.(\d+)\.(\d+)')
    versions = [map(int, v.split('.')) for v in versions if version_regex.match(v)]
    versions.sort(reverse=True)
    return versions[0]


def generate_version():
    if 'nothing to commit' not in subprocess.check_output(["git", "status"]):
        print 'Error: You must commit current changes first'
        exit()

    last_version = get_last_version_from_tags()
    with open('setup.py', 'r') as setup_py_file:
        setup_py = setup_py_file.read()

    new_version = last_version[:]
    new_version[2] += 1
    last_version = '.'.join(map(str, last_version))
    new_version = '.'.join(map(str, new_version))

    print 'upgrading from %s to %s' % (last_version, new_version)

    version_line_re = re.compile(r'''(__version__ =)(\s*['"]\d+\.\d+\.\d+["'])''', flags=re.M)
    with open('setup.py', 'w') as f:
        f.write(version_line_re.sub('\\1 "%s"' % new_version, setup_py))

    subprocess.check_output(["git", 'commit', '-m', '"version %s"' % new_version, '-a'])
    subprocess.check_output(["git", 'tag', '%s' % new_version])

    print
    print 'Version %s created. Push it to origin with "git push --tags"' % new_version

if __name__ == '__main__':
    generate_version()
