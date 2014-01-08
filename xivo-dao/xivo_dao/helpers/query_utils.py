# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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


def paginate(query, paginator):
    '''Paginated the given query with the given paginator.
    - paginator must be a tuple of 2 ints (pahe_no, pagesize).
    - page_no must be strictly positive
    - pagesize must be positive
    If one of these conditions is not fulfilled, all the data will be sent.'''
    (page_no, pagesize) = paginator
    total = query.count()
    if(page_no > 0 and pagesize >= 0):
        offset = (page_no - 1) * pagesize
        paginated_query = query.offset(offset).limit(pagesize)
        items = paginated_query.all()
        return (total, items)
    else:
        items = query.all()
        return (total, items)
