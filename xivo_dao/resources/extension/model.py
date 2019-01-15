# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from collections import namedtuple

ServiceExtension = namedtuple('ServiceExtension', ['id', 'exten', 'service'])
ForwardExtension = namedtuple('ForwardExtension', ['id', 'exten', 'forward'])
AgentActionExtension = namedtuple('AgentActionExtension', ['id', 'exten', 'action'])


class ExtensionDestination(object):
    user = 'user'
    incall = 'incall'
