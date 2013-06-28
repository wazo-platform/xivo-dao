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


class MissingParametersError(ValueError):

    def __init__(self, missing_parameters):
        ValueError.__init__(self, "Missing parameters: %s" % ','.join(missing_parameters))


class InvalidParametersError(ValueError):

    def __init__(self, invalid_parameters):
        ValueError.__init__(self, "Invalid parameters: %s" % ','.join(invalid_parameters))


class ElementExistsError(ValueError):

    def __init__(self, element, *args):
        ValueError.__init__(self, "%s %s already exists" % (element, ' '.join(args)))


class VoicemailExistsException(ValueError):

    def __init__(self):
        ValueError.__init__(self, "Cannot remove a user with a voicemail. Delete the voicemail or dissociate it from the user.")


class ProvdError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "provd error: %s" % self.value
