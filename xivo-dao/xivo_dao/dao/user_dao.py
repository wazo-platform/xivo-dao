from xivo_dao import user_dao
from xivo_dao.models.user import User


def get_user_by_id(user_id):
    return User.from_data_source(user_dao.get(user_id))
