# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.sql.expression import not_

from xivo_dao.alchemy.features import Features
from xivo_dao.asterisk_conf_dao import _PARKING_OPTIONS

FUNC_KEY_FEATUREMAP_FOREIGN_KEY = ['blindxfer', 'automixmon', 'atxfer']


class FeaturesPersistor(object):

    def __init__(self, session):
        self.session = session

    def find_all(self, section):
        query = (self.session.query(Features)
                 .filter(Features.category == section)
                 .filter(Features.var_val != None)  # noqa
                 .order_by(Features.var_metric.asc()))

        if section == 'general':
            query = query.filter(not_(Features.var_name.in_(_PARKING_OPTIONS)))

        return query.all()

    def edit_all(self, section, features):
        self._fill_default_values(section, features)
        self._delete_all_section(section)
        features = self._update_existing_foreign_key_features(features)
        self.session.add_all(features)
        self.session.flush()

    def _fill_default_values(self, section, features):
        for setting in features:
            setting.filename = 'features.conf'
            setting.category = section
        return features

    def _delete_all_section(self, section):
        query = (self.session.query(Features)
                 .filter(Features.category == section))
        if section == 'general':
            query = query.filter(not_(Features.var_name.in_(_PARKING_OPTIONS)))

        if section == 'featuremap':
            query = query.filter(not_(Features.var_name.in_(FUNC_KEY_FEATUREMAP_FOREIGN_KEY)))

        query.delete(synchronize_session=False)

    def _update_existing_foreign_key_features(self, features):
        query = (self.session.query(Features)
                 .filter(Features.category == 'featuremap')
                 .filter(Features.var_name.in_(FUNC_KEY_FEATUREMAP_FOREIGN_KEY)))
        old_features = query.all()

        results = []
        for feature in features:
            results.append(feature)
            for old_feature in old_features:
                if old_feature.category == feature.category and old_feature.var_name == feature.var_name:
                    old_feature.var_val = feature.var_val
                    self._fix_commented(old_feature)
                    results.remove(feature)
        return results

    def _fix_commented(self, feature):
        feature.commented = 0
