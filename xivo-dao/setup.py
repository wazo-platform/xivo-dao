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
        'xivo_dao.converters',
        'xivo_dao.data_handler',
        'xivo_dao.data_handler.call_log',
        'xivo_dao.data_handler.cel',
        'xivo_dao.data_handler.context',
        'xivo_dao.data_handler.device',
        'xivo_dao.data_handler.extension',
        'xivo_dao.data_handler.language',
        'xivo_dao.data_handler.line',
        'xivo_dao.data_handler.user',
        'xivo_dao.data_handler.user_line',
        'xivo_dao.data_handler.user_line_extension',
        'xivo_dao.data_handler.user_voicemail',
        'xivo_dao.data_handler.voicemail',
        'xivo_dao.helpers',
    ]
)
