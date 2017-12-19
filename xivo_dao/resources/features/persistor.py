# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.features import Features


class FeaturesPersistor(object):

    def __init__(self, session):
        self.session = session

    def find_all(self, section):
        query = (self.session.query(Features)
                 .filter(Features.category == section)
                 .filter(Features.var_val != None)  # noqa
                 .order_by(Features.var_metric.asc()))
        return query.all()

    def edit_all(self, features):
        self.session.query(Features).delete()
        self.session.add_all(self._fill_default_values(features))
        self.session.flush()

    def _fill_default_values(self, features):
        for setting in features:
            setting.filename = 'features.conf'
        return features
