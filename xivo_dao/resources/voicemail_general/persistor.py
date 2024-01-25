# Copyright 2017-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.staticvoicemail import StaticVoicemail


class VoicemailGeneralPersistor:
    def __init__(self, session):
        self.session = session

    def find_all(self):
        query = (
            self.session.query(StaticVoicemail)
            .filter(StaticVoicemail.category == 'general')
            .filter(StaticVoicemail.var_val != None)  # noqa
            .order_by(StaticVoicemail.var_metric.asc())
        )
        return query.all()

    def edit_all(self, voicemail_general):
        self.session.query(StaticVoicemail).filter(
            StaticVoicemail.category == 'general'
        ).delete()
        self.session.add_all(self._fill_default_values(voicemail_general))
        self.session.flush()

    def _fill_default_values(self, voicemail_general):
        for var_metric, setting in enumerate(voicemail_general):
            setting.filename = 'voicemail.conf'
            setting.category = 'general'
        return voicemail_general
