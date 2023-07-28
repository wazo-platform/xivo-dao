# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from typing import NamedTuple


class ServiceFeatureExtension(NamedTuple):
    uuid: str
    exten: str
    service: str


class ForwardFeatureExtension(NamedTuple):
    uuid: str
    exten: str
    forward: str


class AgentActionFeatureExtension(NamedTuple):
    uuid: str
    exten: str
    action: str
