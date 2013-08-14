# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_dao.data_handler.exception import InvalidParametersError


class AbstractModels(object):

    def __init__(self, **kwargs):
        self.update_from_data(kwargs)

    def __eq__(self, other):
        class_name = self.__class__.__name__
        if not isinstance(other, self.__class__):
            raise TypeError('Must compare a %s with another %s' % (class_name, class_name))

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other

    @classmethod
    def from_data_source(cls, db_object):
        obj = cls()
        for db_field, model_field in obj._MAPPING.iteritems():
            if hasattr(db_object, db_field):
                model_field_value = getattr(db_object, db_field)
                setattr(obj, model_field, model_field_value)
        for db_field, model_field in obj._RELATION.iteritems():
            if hasattr(db_object, db_field):
                model_field_value = getattr(db_object, db_field)
                setattr(obj, model_field, model_field_value)
        return obj

    def update_from_data_source(self, db_object):
        for db_field, model_field in self._MAPPING.iteritems():
            if hasattr(db_object, db_field):
                if db_field == 'id':
                    continue
                model_field_value = getattr(db_object, db_field)
                setattr(self, model_field, model_field_value)

    def to_data_source(self, class_schema):
        db_object = class_schema()
        for db_field, model_field in self._MAPPING.iteritems():
            if hasattr(self, model_field):
                field_value = getattr(self, model_field)
                setattr(db_object, db_field, field_value)
        return db_object

    def update_data_source(self, db_object):
        for db_field, model_field in self._MAPPING.iteritems():
            if hasattr(self, model_field):
                if db_field == 'id':
                    continue
                model_field_value = getattr(self, model_field)
                setattr(db_object, db_field, model_field_value)

    def update_from_data(self, data):
        parameters = data.keys()
        invalid = self.invalid_parameters(parameters)

        if len(invalid) > 0:
            raise InvalidParametersError(invalid)

        for model_field in self._MAPPING.itervalues():
            model_field_value = data.get(model_field)
            if model_field_value is not None:
                setattr(self, model_field, model_field_value)
        for model_field in self._RELATION.itervalues():
            model_field_value = data.get(model_field)
            if model_field_value is not None:
                setattr(self, model_field, model_field_value)

    def to_data_dict(self):
        data_dict = {}
        for db_field, model_field in self._MAPPING.iteritems():
            if hasattr(self, model_field):
                field_value = getattr(self, model_field)
                data_dict[db_field] = field_value
        return data_dict

    @classmethod
    def from_user_data(cls, properties):
        return cls(**properties)

    def invalid_parameters(self, parameters):
        allowed = self._MAPPING.values() + self._RELATION.values()
        return set(parameters).difference(set(allowed))

    def missing_parameters(self):
        missing = []

        for parameter in self.MANDATORY:
            try:
                attribute = getattr(self, parameter)
                if attribute is None:
                    missing.append(parameter)
            except AttributeError:
                missing.append(parameter)

        return missing
