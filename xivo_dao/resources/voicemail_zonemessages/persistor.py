# Copyright 2017-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.staticvoicemail import StaticVoicemail


class VoicemailZoneMessagesPersistor:
    def __init__(self, session):
        self.session = session

    def find_all(self):
        query = (
            self.session.query(StaticVoicemail)
            .filter(StaticVoicemail.category == 'zonemessages')
            .filter(StaticVoicemail.var_val != None)  # noqa
        )
        return query.all()

    def edit_all(self, voicemail_zonemessages):
        self.session.query(StaticVoicemail).filter(
            StaticVoicemail.category == 'zonemessages'
        ).delete()
        self.session.add_all(self._fill_default_values(voicemail_zonemessages))
        self.session.flush()

    def _fill_default_values(self, voicemail_zonemessages):
        for setting in voicemail_zonemessages:
            setting.cat_metric = 1
            setting.filename = 'voicemail.conf'
            setting.category = 'zonemessages'
        return voicemail_zonemessages
