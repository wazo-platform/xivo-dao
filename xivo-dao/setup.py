#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from distutils.core import setup

setup(
    name='xivo-dao',
    version='0.1',
    description='XiVO Data Access Object',
    author='Avencall',
    author_email='dev@avencall.com',
    url='http://git.xivo.fr/',
    license='GPLv3',
    packages=[
        'xivo_dao',
        'xivo_dao.alchemy',
        'xivo_dao.dao',
        'xivo_dao.helpers',
        'xivo_dao.models',
        'xivo_dao.notifiers',
        'xivo_dao.service_data_model',
        'xivo_dao.services',
    ]
)
