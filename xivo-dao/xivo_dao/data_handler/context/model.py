from xivo_dao.helpers.abstract_model import AbstractModels


class ContextType(object):
    incall = 'incall'
    internal = 'internal'
    other = 'others'
    outcall = 'outcall'
    service = 'services'

    @classmethod
    def all(cls):
        return [cls.incall, cls.internal, cls.other, cls.outcall, cls.service]


class Context(AbstractModels):

    MANDATORY = [
        'name',
        'display_name',
        'type'
    ]

    # mapping = {db_field: model_field}
    _MAPPING = {
        'name': 'name',
        'displayname': 'display_name',
        'description': 'description',
        'contexttype': 'type'
    }

    _RELATION = {
    }
