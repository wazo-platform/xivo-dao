# Copyright 2023-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm import joinedload

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.schedule import Schedule
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.alchemy.userfeatures import UserFeatures

incall_preload_relationships = (
    joinedload(Incall.caller_id),
    joinedload(Incall.dialaction).options(
        joinedload(Dialaction.conference),
        joinedload(Dialaction.group),
        joinedload(Dialaction.user).load_only(
            UserFeatures.firstname, UserFeatures.webi_lastname
        ),
        joinedload(Dialaction.ivr),
        joinedload(Dialaction.ivr_choice),
        joinedload(Dialaction.switchboard),
        joinedload(Dialaction.voicemail),
        joinedload(Dialaction.application),
        joinedload(Dialaction.queue),
    ),
    joinedload(Incall.extensions)
    .load_only(Extension.id, Extension.exten)
    .selectinload(Extension.context_rel),
    joinedload(Incall.schedule_paths)
    .selectinload(SchedulePath.schedule)
    .load_only(Schedule.id, Schedule.name),
)
