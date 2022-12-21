# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from collections import namedtuple

ServiceExtension = namedtuple('ServiceExtension', ['id', 'exten', 'service'])
ForwardExtension = namedtuple('ForwardExtension', ['id', 'exten', 'forward'])
AgentActionExtension = namedtuple('AgentActionExtension', ['id', 'exten', 'action'])
