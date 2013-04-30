from xivo_dao.dao import voicemail as voicemail_dao


class VoicemailNotFoundException(LookupError):

    @classmethod
    def from_number(cls, number):
        message = "Voicemail with number %s does not exist" % number
        return cls(message)


def delete(**kwargs):
    if 'number' in kwargs:
        delete_by_number(kwargs['number'])


def delete_by_number(number):
    voicemail = voicemail_dao.find_by_number(number)
    if not voicemail:
        raise VoicemailNotFoundException.from_number(number)

    voicemail_dao.delete(voicemail)
