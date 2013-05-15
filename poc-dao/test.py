from __future__ import unicode_literals

from xivo_ws import XivoServer, User, UserLine, UserVoicemail

from xivo_dao.services import voicemail_services
from xivo_dao.dao.voicemail_dao import Voicemail

import psycopg2

WS_IP = 'localhost'
WS_USERNAME = 'admin'
WS_PASSWORD = 'proformatique'

DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'asterisk'
DB_USER = 'asterisk'
DB_PASSWORD = 'proformatique'

connection = psycopg2.connect(host=DB_HOST,
                              port=int(DB_PORT),
                              database=DB_NAME,
                              user=DB_USER,
                              password=DB_PASSWORD)


def delete_user_and_voicemail(number):
    server = XivoServer(WS_IP, WS_USERNAME, WS_PASSWORD)
    users = server.users.search(number)

    for user in users:
        if user.voicemail:
            server.voicemails.delete(user.voicemail.id)
        server.users.delete(user.id)


def delete_voicemail(number):
    server = XivoServer(WS_IP, WS_USERNAME, WS_PASSWORD)
    voicemails = server.voicemails.search(number)
    for voicemail in voicemails:
        server.voicemails.delete(voicemail.id)


def create_user_and_voicemail(number_sip, number_sccp):
    server = XivoServer(WS_IP, WS_USERNAME, WS_PASSWORD)

    user_sip = build_sip_user(number_sip)
    user_sccp = build_sccp_user(number_sccp)

    user_sip_id = server.users.add(user_sip)
    user_sccp_id = server.users.add(user_sccp)
    return (int(user_sip_id), int(user_sccp_id))


def build_sip_user(number):
    user = User(firstname='voicemail', lastname='usersip', language='fr_FR')

    user_line = UserLine(protocol='sip', context='default', number=number)

    user_voicemail = UserVoicemail(number=number, name='voicemail usersip')

    user.line = user_line
    user.voicemail = user_voicemail

    return user


def build_sccp_user(number):
    user = User(firstname='voicemail', lastname='usersccp', language='fr_FR')

    user_line = UserLine(protocol='sccp', context='default', number=number)

    user_voicemail = UserVoicemail(number=number, name='voicemail usersccp')

    user.line = user_line
    user.voicemail = user_voicemail

    return user


def check_database_tables(user_id, number):

    check_voicemail(number)
    check_userfeatures(user_id)
    check_usersip(number)


def check_voicemail(number):
    query = "SELECT COUNT(*) FROM voicemail WHERE mailbox = %s"
    cursor = connection.cursor()
    cursor.execute(query, (number,))

    count = cursor.fetchone()[0]

    assert count == 0, "voicemail was not deleted"


def check_userfeatures(user_id):
    query = "SELECT voicemailid FROM userfeatures WHERE id = %s"
    cursor = connection.cursor()
    cursor.execute(query, (user_id,))

    voicemail_id = cursor.fetchone()[0]

    assert voicemail_id is None, "voicemail was not deleted in userfeatures"


def check_usersip(number):
    query = "SELECT COUNT(*) FROM usersip WHERE mailbox = %s"
    cursor = connection.cursor()

    full_number = '%s@default' % number
    cursor.execute(query, (full_number,))

    count = cursor.fetchone()[0]

    assert count == 0, "voicemail was not deleted in usersip"


def check_voicemail_created(voicemail):
    query = "SELECT mailbox, context, fullname FROM voicemail WHERE mailbox = %s AND context = %s"
    cursor = connection.cursor()

    cursor.execute(query, (voicemail.number, voicemail.context))

    row = cursor.fetchone()

    assert row is not None, "voicemail was not created"

    assert row[0] == voicemail.number, "wrong voicemail number, %s instead of %s" % (row[0], voicemail.number)
    assert row[1] == voicemail.context, "wrong voicemail context, %s instead of %s" % (row[1], voicemail.context)
    assert row[2] == voicemail.name, "wrong voicemail name, %s instead of %s" % (row[2], voicemail.name)

if __name__ == "__main__":
    number_sip = '1300'
    number_sccp = '1301'
    context = 'default'

    print "deleting user and voicemail..."
    delete_user_and_voicemail(number_sip)
    delete_user_and_voicemail(number_sccp)

    print "creating user and voicemail..."
    (user_sip_id, user_sccp_id) = create_user_and_voicemail(number_sip, number_sccp)
    voicemail_services.delete(number_sip, context)
    voicemail_services.delete(number_sccp, context)

    print "checking database tables..."
    check_database_tables(user_sip_id, number_sip)
    check_database_tables(user_sccp_id, number_sccp)

    print "----------------------------------------"
    number = '1310'
    context = 'default'
    name = 'voicemail name'

    print "deleting voicemail"
    delete_voicemail(number)

    voicemail = Voicemail(
        number=number,
        context=context,
        name=name
    )

    print "creating voicemail"
    voicemail_services.create(voicemail)

    print "checking database tables"
    check_voicemail_created(voicemail)
