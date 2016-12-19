# -*- coding: utf-8 -*-

# Copyright 2013-2016 The Wazo Authors  (see the AUTHORS file)
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

from xivo_dao.alchemy.extension import Extension
from xivo_dao.helpers.db_manager import Session

from xivo_dao.resources.extension.persistor import ExtensionPersistor
from xivo_dao.resources.extension.database import \
    fwd_converter, service_converter, agent_action_converter
from xivo_dao.resources.extension.fixes import ExtensionFixes


def persistor():
    return ExtensionPersistor(Session)


def get_by(**criteria):
    return persistor().get_by(criteria)


def find_by(**criteria):
    return persistor().find_by(criteria)


def find_all_by(**criteria):
    return persistor().find_all_by(criteria)


def get(id):
    return persistor().get_by({'id': id})


def find(id):
    return persistor().find_by({'id': id})


def search(**parameters):
    return persistor().search(parameters)


def create(extension):
    return persistor().create(extension)


def edit(extension):
    persistor().edit(extension)
    ExtensionFixes(Session).fix(extension.id)


def delete(extension):
    persistor().delete(extension)


def associate_incall(incall, extension):
    persistor().associate_incall(incall, extension)
    ExtensionFixes(Session).fix(extension.id)


def dissociate_incall(incall, extension):
    persistor().dissociate_incall(incall, extension)
    ExtensionFixes(Session).fix(extension.id)


def associate_group(group, extension):
    persistor().associate_group(group, extension)
    group.fix_extension()


def dissociate_group(group, extension):
    persistor().dissociate_group(group, extension)
    group.fix_extension()


def associate_conference(conference, extension):
    persistor().associate_conference(conference, extension)


def dissociate_conference(conference, extension):
    persistor().dissociate_conference(conference, extension)


def associate_parking_lot(parking_lot, extension):
    persistor().associate_parking_lot(parking_lot, extension)


def dissociate_parking_lot(parking_lot, extension):
    persistor().dissociate_parking_lot(parking_lot, extension)


def find_all_service_extensions():
    typevals = service_converter.typevals()
    query = (Session.query(Extension.id,
                           Extension.exten,
                           Extension.typeval)
             .filter(Extension.type == 'extenfeatures')
             .filter(Extension.typeval.in_(typevals))
             )

    return [service_converter.to_model(row) for row in query]


def find_all_forward_extensions():
    typevals = fwd_converter.typevals()
    query = (Session.query(Extension.id,
                           Extension.exten,
                           Extension.typeval)
             .filter(Extension.type == 'extenfeatures')
             .filter(Extension.typeval.in_(typevals))
             )

    return [fwd_converter.to_model(row) for row in query]


def find_all_agent_action_extensions():
    typevals = agent_action_converter.typevals()
    query = (Session.query(Extension.id,
                           Extension.exten,
                           Extension.typeval)
             .filter(Extension.type == 'extenfeatures')
             .filter(Extension.typeval.in_(typevals))
             )

    return [agent_action_converter.to_model(row) for row in query]
