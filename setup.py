#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import fnmatch
import os

from setuptools import setup
from setuptools import find_packages


setup(
    name='xivo-dao',
    version='0.1',
    description='XiVO Data Access Object',
    author='Avencall',
    author_email='dev@avencall.com',
    url='http://git.xivo.io/',
    license='GPLv3',
    packages=find_packages(),
)
