# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

from functools import wraps
from mock import patch
from mock import Mock


def mocked_dao_session(f):
    '''
    Injects a mocked DAO session in the decorated function's arguments.
    The injected DAO session is inserted as the last argument.
    '''
    @wraps(f)
    def wrapped(*args, **kwargs):
        mocked_session = Mock(name='dao_session_mock')
        with patch('xivo_dao.helpers.db_manager._DaoSession', Mock(return_value=mocked_session)):
            new_args = list(args)
            new_args.append(mocked_session)
            return f(*new_args, **kwargs)
    return wrapped
