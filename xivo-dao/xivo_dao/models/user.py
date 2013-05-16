class User(object):
    def __init__(self, **kwargs):
        pass

    @classmethod
    def from_data_source(cls, properties):
        new_instance = cls()
        new_instance.id = properties.id
        return new_instance
