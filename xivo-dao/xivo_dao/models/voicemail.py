class Voicemail(object):

    MANDATORY = ['name',
                 'number',
                 'context']

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.number = kwargs.get('number')
        self.context = kwargs.get('context')
        self.id = kwargs.get('id')
        self.user = kwargs.get('user')

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError("Must compare Voicemail with another Voicemail")
        return (self.name == other.name
                and self.number == other.number
                and self.context == other.context
                and self.id == other.id
                and self.user == other.user)

    @classmethod
    def from_data_source(cls, properties):
        voicemail = cls()
        voicemail.name = properties.fullname
        voicemail.number = properties.mailbox
        voicemail.context = properties.context
        voicemail.id = properties.uniqueid
        return voicemail

    @classmethod
    def from_user_data(cls, properties):
        voicemail = cls(**properties)
        return voicemail

    @property
    def number_at_context(self):
        return '%s@%s' % (self.number, self.context)

    def missing_parameters(self):
        missing = []

        for parameter in self.MANDATORY:
            attribute = getattr(self, parameter)
            if attribute is None:
                missing.append(parameter)

        return missing
