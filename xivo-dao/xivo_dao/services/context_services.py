from xivo_dao import context_dao


def find_by_name(context_name):
    return context_dao.get(context_name)
