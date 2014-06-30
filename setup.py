#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import fnmatch
import os

from distutils.core import setup


def is_package(path):
    is_svn_dir = fnmatch.fnmatch(path, '*/.svn*')
    is_test_module = fnmatch.fnmatch(path, '*tests')
    return not (is_svn_dir or is_test_module)

packages = [p for p, _, _ in os.walk('xivo_dao') if is_package(p)]
setup(
    name='xivo-dao',
    version='0.1',
    description='XiVO Data Access Object',
    author='Avencall',
    author_email='dev@avencall.com',
    url='http://git.xivo.io/',
    license='GPLv3',
    packages=packages,
)
