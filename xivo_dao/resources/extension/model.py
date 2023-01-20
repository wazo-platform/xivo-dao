# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from typing import NamedTuple


class ServiceExtension(NamedTuple):
    id: int
    exten: str
    service: str


class ForwardExtension(NamedTuple):
    id: int
    exten: str
    forward: str


class AgentActionExtension(NamedTuple):
    id: int
    exten: str
    action: str
