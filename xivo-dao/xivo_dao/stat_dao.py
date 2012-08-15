# -*- coding: utf-8 -*-

from xivo_dao.alchemy.dbconnection import get_connection

_STR_TIME_FMT = "%Y-%m-%d %H:%M:%S.%f"


def _get_session():
    return get_connection('asterisk').get_session()


def fill_saturated_calls(start, end):
    start = start.strftime(_STR_TIME_FMT)
    end = end.strftime(_STR_TIME_FMT)

    (_get_session()
     .query('place_holder')
     .from_statement(
            'SELECT 1 AS place_holder FROM fill_saturated_calls(:start, :end)'
            )
     .params(start=start, end=end)
     .first())
