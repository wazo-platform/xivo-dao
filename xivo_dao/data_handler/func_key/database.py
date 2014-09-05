from sqlalchemy import func

from xivo_dao.converters.database_converter import DatabaseConverter
from xivo_dao.data_handler.func_key import type_dao as func_key_type_dao
from xivo_dao.data_handler.func_key.model import FuncKey
from xivo_dao.data_handler.utils.search import SearchSystem, SearchConfig

from xivo_dao.alchemy.func_key import FuncKey as FuncKeySchema
from xivo_dao.alchemy.func_key_type import FuncKeyType as FuncKeyTypeSchema
from xivo_dao.alchemy.func_key_dest_user import FuncKeyDestUser as FuncKeyDestUserSchema
from xivo_dao.alchemy.func_key_dest_group import FuncKeyDestGroup as FuncKeyDestGroupSchema
from xivo_dao.alchemy.func_key_dest_queue import FuncKeyDestQueue as FuncKeyDestQueueSchema
from xivo_dao.alchemy.func_key_dest_conference import FuncKeyDestConference as FuncKeyDestConferenceSchema
from xivo_dao.alchemy.func_key_dest_forward import FuncKeyDestForward as FuncKeyDestForwardSchema
from xivo_dao.alchemy.func_key_dest_service import FuncKeyDestService as FuncKeyDestServiceSchema
from xivo_dao.alchemy.func_key_destination_type import FuncKeyDestinationType as FuncKeyDestinationTypeSchema


class QueryHelper(object):

    column_mapping = {
        'id': FuncKeySchema.id.label('id'),
        'type': FuncKeyTypeSchema.name.label('type'),
        'destination': FuncKeyDestinationTypeSchema.name.label('destination'),
        'destination_id': func.coalesce(FuncKeyDestUserSchema.user_id,
                                        FuncKeyDestGroupSchema.group_id,
                                        FuncKeyDestQueueSchema.queue_id,
                                        FuncKeyDestConferenceSchema.conference_id,
                                        FuncKeyDestServiceSchema.extension_id,
                                        FuncKeyDestForwardSchema.extension_id,
                                        ).label('destination_id')
    }

    destination_mapping = {
        'user': (FuncKeyDestUserSchema, FuncKeyDestUserSchema.user_id),
        'group': (FuncKeyDestGroupSchema, FuncKeyDestGroupSchema.group_id),
        'queue': (FuncKeyDestQueueSchema, FuncKeyDestQueueSchema.queue_id),
        'conference': (FuncKeyDestConferenceSchema, FuncKeyDestConferenceSchema.conference_id),
        'service': (FuncKeyDestServiceSchema, FuncKeyDestServiceSchema.extension_id),
        'forward': (FuncKeyDestForwardSchema, FuncKeyDestForwardSchema.extension_id),
    }

    @classmethod
    def destination_exists(cls, destination):
        return destination in cls.destination_mapping

    def __init__(self, session):
        self._session = session

    def search(self, parameters):
        config = SearchConfig(table=FuncKeySchema,
                              columns=self.column_mapping,
                              default_sort='id')

        return SearchSystem(config).search_from_query(self.query(), parameters)

    def select_destination(self, destination, destination_id):
        schema, column = self.destination_mapping[destination]
        return self.query().filter(column == destination_id)

    def select_func_key(self, func_key_id):
        return self.query().filter(FuncKeySchema.id == func_key_id)

    def delete_destination(self, destination, destination_id):
        schema, column = self.destination_mapping[destination]
        return self._session.query(schema).filter(column == destination_id)

    def delete_func_key(self, func_key_id):
        return self._session.query(FuncKeySchema).filter(FuncKeySchema.id == func_key_id)

    def query(self):
        destination_id_col = self.column_mapping['destination_id']
        return (self._session
                .query(self.column_mapping['id'],
                       self.column_mapping['type'],
                       self.column_mapping['destination'],
                       self.column_mapping['destination_id'])
                .join(FuncKeyTypeSchema, FuncKeySchema.type_id == FuncKeyTypeSchema.id)
                .join(FuncKeyDestinationTypeSchema)
                .outerjoin(FuncKeyDestUserSchema, FuncKeyDestUserSchema.func_key_id == FuncKeySchema.id)
                .outerjoin(FuncKeyDestGroupSchema, FuncKeyDestGroupSchema.func_key_id == FuncKeySchema.id)
                .outerjoin(FuncKeyDestQueueSchema, FuncKeyDestQueueSchema.func_key_id == FuncKeySchema.id)
                .outerjoin(FuncKeyDestConferenceSchema, FuncKeyDestConferenceSchema.func_key_id == FuncKeySchema.id)
                .outerjoin(FuncKeyDestServiceSchema, FuncKeyDestServiceSchema.func_key_id == FuncKeySchema.id)
                .outerjoin(FuncKeyDestForwardSchema, FuncKeyDestForwardSchema.func_key_id == FuncKeySchema.id)
                .filter(destination_id_col != None))


class FuncKeyOrder(object):
    id = QueryHelper.column_mapping['id']
    type = QueryHelper.column_mapping['type']
    destination = QueryHelper.column_mapping['destination']
    destination_id = QueryHelper.column_mapping['destination_id']


class FuncKeyDbConverter(DatabaseConverter):

    DB_TO_MODEL_MAPPING = {
        'id': 'id',
        'type': 'type',
        'destination': 'destination',
        'destination_id': 'destination_id',
    }

    destination_mapping = {
        'user': (FuncKeyDestUserSchema, 'user_id'),
        'group': (FuncKeyDestGroupSchema, 'group_id'),
        'queue': (FuncKeyDestQueueSchema, 'queue_id'),
        'conference': (FuncKeyDestConferenceSchema, 'conference_id'),
        'service': (FuncKeyDestServiceSchema, 'extension_id'),
        'forward': (FuncKeyDestForwardSchema, 'extension_id'),
    }

    def __init__(self):
        DatabaseConverter.__init__(self,
                                   self.DB_TO_MODEL_MAPPING,
                                   FuncKeySchema,
                                   FuncKey)

    def create_func_key_row(self, model):
        destination_type_row = func_key_type_dao.find_destination_type_for_name(model.destination)
        type_row = func_key_type_dao.find_type_for_name(model.type)

        func_key_row = FuncKeySchema(type_id=type_row.id,
                                     destination_type_id=destination_type_row.id)

        return func_key_row

    def create_destination_row(self, model):
        destination_type_row = func_key_type_dao.find_destination_type_for_name(model.destination)

        schema, column_name = self.destination_mapping[model.destination]
        destination_row = schema(destination_type_id=destination_type_row.id,
                                 func_key_id=model.id)
        setattr(destination_row, column_name, model.destination_id)

        return destination_row


db_converter = FuncKeyDbConverter()
