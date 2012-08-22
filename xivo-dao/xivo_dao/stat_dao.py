# -*- coding: utf-8 -*-

from xivo_dao.alchemy.dbconnection import get_connection

_STR_TIME_FMT = "%Y-%m-%d %H:%M:%S.%f"


def _get_session():
    return get_connection('asterisk').get_session()


def fill_simple_calls(start, end):
    _run_sql_function_returning_void(
        start, end,
        'SELECT 1 AS place_holder FROM fill_simple_calls(:start, :end)'
        )


def fill_answered_calls(start, end):
    _run_sql_function_returning_void(
        start, end,
        'SELECT 1 AS place_holder FROM fill_answered_calls(:start, :end)'
        )


def fill_leaveempty_calls(start, end):
    _run_sql_function_returning_void(
        start, end,
        'SELECT 1 AS place_holder FROM fill_leaveempty_calls(:start, :end)'
        )


def _run_sql_function_returning_void(start, end, function):
    start = start.strftime(_STR_TIME_FMT)
    end = end.strftime(_STR_TIME_FMT)

    (_get_session()
     .query('place_holder')
     .from_statement(function)
     .params(start=start, end=end)
     .first())
