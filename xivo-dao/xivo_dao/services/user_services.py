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

from xivo_dao.dao import user_dao
from xivo_dao.notifiers import bus_notifier, sysconf_notifier
from xivo_dao.services.exception import MissingParametersError, \
    InvalidParametersError, ElementExistsError
from xivo_dao.services import voicemail_services
from xivo_dao.models.voicemail import Voicemail


class UserNotFoundError(LookupError):

    @classmethod
    def from_user_id(cls, user_id):
        message = "User %s does not exist" % (user_id)
        return cls(message)


def get_by_user_id(user_id):
    return user_dao.get_user_by_id(user_id)


def find_all():
    return user_dao.find_all()


def find_by_firstname_lastname(firstname, lastname):
    return user_dao.find_user(firstname, lastname)


def create(user):
    _validate(user)
    _check_for_existing_user(user)
    user_id = user_dao.create(user)
    bus_notifier.user_created(user_id)
    sysconf_notifier.create_user(user_id)
    return user_id


def edit(user):
    _validate(user)
    user_dao.edit(user)
    bus_notifier.user_updated(user.id)
    sysconf_notifier.edit_user(user.id)


def delete(user):
    user_dao.delete(user)
    voicemail_services.delete(user.voicemail)
    bus_notifier.user_deleted(user.id)
    sysconf_notifier.delete_user(user.id)

"""
    try:
    except ProvdError as e:
        result = "The user was deleted but the device could not be reconfigured (%s)" % str(e)
        result = rest_encoder.encode([result])
        return make_response(result, 500)
    except VoicemailExistsException:
        result = "Cannot remove a user with a voicemail. Delete the voicemail or dissociate it from the user."
        result = rest_encoder.encode([result])
        return make_response(result, 412)
    except SysconfdError as e:
        result = "The user was deleted but the voicemail content could not be removed (%s)" % str(e)
        result = rest_encoder.encode([result])
        return make_response(result, 500)


def _provd_remove_line(self, deviceid, linenum):
    config = self.config_manager.get(deviceid)
    del config["raw_config"]["sip_lines"][str(linenum)]
    if len(config["raw_config"]["sip_lines"]) == 0:
        # then we reset to autoprov
        self._reset_config(config)
        self._reset_device_to_autoprov(deviceid)
    self.config_manager.update(config)


def _reset_config(self, config):
    del config["raw_config"]["sip_lines"]
    if "funckeys" in config["raw_config"]:
        del config["raw_config"]["funckeys"]


def _reset_device_to_autoprov(self, deviceid):
    device = self.device_manager.get(deviceid)
    new_configid = self.config_manager.autocreate()
    device["config"] = new_configid
    self.device_manager.update(device)


def _remove_line(self, line):
    device = line.device
    line_dao.delete(line.id)
    deviceid = device_dao.get_deviceid(device)
    if deviceid is not None:
        try:
            self._provd_remove_line(deviceid, line.num)
        except URLError as e:
            raise ProvdError(str(e))


def _delete_voicemail(self, voicemailid):
    voicemail = voicemail_dao.get(voicemailid)
    context, mailbox = voicemail.context, voicemail.mailbox
    voicemail_dao.delete(voicemailid)
    try:
        self.sysconfd_connector.delete_voicemail_storage(context, mailbox)
    except Exception as e:
        raise SysconfdError(str(e))
"""


def _validate(user):
    _check_missing_parameters(user)
    _check_invalid_parameters(user)


def _check_missing_parameters(user):
    missing = user.missing_parameters()
    if missing:
        raise MissingParametersError(missing)


def _check_invalid_parameters(user):
    invalid_parameters = []
    if not user.firstname:
        invalid_parameters.append('firstname')
    if invalid_parameters:
        raise InvalidParametersError(invalid_parameters)


def _check_for_existing_user(user):
    if user_dao.find_user(user.firstname, user.lastname):
        raise ElementExistsError('User', user.firstname, user.lastname)


def _update_voicemail_fullname(user):
    voicemail_id = user.voicemail
    if voicemail_id is not None:
        voicemail = Voicemail.from_user_data({'fullname': user.fullname})
        voicemail_services.edit(voicemail_id, voicemail)
