from xivo_dao.converters.database_converter import DatabaseConverter
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.data_handler.user.model import User


class UserDbConverter(DatabaseConverter):

    DB_TO_MODEL_MAPPING = {
        'id': 'id',
        'firstname': 'firstname',
        'lastname': 'lastname',
        'outcallerid': 'outgoing_caller_id',
        'loginclient': 'username',
        'passwdclient': 'password',
        'musiconhold': 'music_on_hold',
        'mobilephonenumber': 'mobile_phone_number',
        'userfield': 'userfield',
        'timezone': 'timezone',
        'language': 'language',
        'description': 'description',
        'voicemailid': 'voicemail_id',
        'preprocess_subroutine': 'preprocess_subroutine',
        'func_key_private_template_id': 'private_template_id',
    }

    def __init__(self):
        DatabaseConverter.__init__(self, self.DB_TO_MODEL_MAPPING, UserSchema, User)

    def to_model(self, source):
        model = DatabaseConverter.to_model(self, source)
        self._convert_model_fields(source, model)

        return model

    def _convert_model_fields(self, source, model):
        model.caller_id = source.callerid

        if model.password == '':
            model.password = None
        if model.mobile_phone_number == '':
            model.mobile_phone_number = None

    def update_source(self, source, model):
        DatabaseConverter.update_source(self, source, model)
        self._convert_source_fields(source, model)

    def to_source(self, model):
        source = DatabaseConverter.to_source(self, model)
        self._convert_source_fields(source, model)
        return source

    def _convert_source_fields(self, source, model):
        source.callerid = model.generate_caller_id()

        if source.passwdclient is None:
            source.passwdclient = ''
        if source.mobilephonenumber is None:
            source.mobilephonenumber = ''


db_converter = UserDbConverter()
