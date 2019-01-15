# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import six


class DatabaseConverter(object):

    def __init__(self, mapping, schema, model):
        self.schema = schema
        self.model = model

        model_mapping = dict((value, key) for key, value in six.iteritems(mapping))

        self.db_mapping = mapping
        self.model_mapping = model_mapping

    def to_model(self, db_row):
        db_columns = self._extract_columns(db_row, self.db_mapping.keys())
        model_columns = self._remap_columns(db_columns, self.db_mapping)
        return self.model(**model_columns)

    def to_source(self, model):
        model_columns = self._extract_columns(model, self.model_mapping.keys())
        db_columns = self._remap_columns(model_columns, self.model_mapping)
        return self.schema(**db_columns)

    def update_model(self, model, db_row):
        db_columns = self._extract_columns(db_row, self.db_mapping.keys())
        model_columns = self._remap_columns(db_columns, self.db_mapping)
        self._update_object(model_columns, model)

    def update_source(self, db_row, model):
        model_columns = self._extract_columns(model, self.model_mapping.keys())
        db_columns = self._remap_columns(model_columns, self.model_mapping)
        self._update_object(db_columns, db_row)

    def _extract_columns(self, source_object, columns):
        extracted_values = {}
        for column_name in columns:
            if not hasattr(source_object, column_name):
                raise ValueError('column %s does not exist in object %s' % (column_name, type(source_object)))
            extracted_values[column_name] = getattr(source_object, column_name)
        return extracted_values

    def _remap_columns(self, columns, mapping):
        mapped_columns = {}
        for column_name, value in six.iteritems(columns):
            key = mapping[column_name]
            mapped_columns[key] = value
        return mapped_columns

    def _update_object(self, values, destination):
        for key, value in six.iteritems(values):
            setattr(destination, key, value)
