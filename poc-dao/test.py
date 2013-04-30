from __future__ import unicode_literals

from xivo_ws import XivoServer, User, UserLine, UserVoicemail

#from dao.services import voicemail

import psycopg2

WS_IP = '10.42.0.1'
WS_USERNAME = 'admin'
WS_PASSWORD = 'proformatique'

DB_HOST = '10.42.0.1'
DB_PORT = '5432'
DB_NAME = 'asterisk'
DB_USER = 'asterisk'
DB_PASSWORD = 'proformatique'


def delete_user_and_voicemail(extension):
    server = XivoServer(WS_IP, WS_USERNAME, WS_PASSWORD)
    users = server.users.search(extension)

    for user in users:
        if user.voicemail:
            server.voicemails.delete(user.voicemail.id)
        server.users.delete(user.id)


def create_user_and_voicemail(extension):
    server = XivoServer(WS_IP, WS_USERNAME, WS_PASSWORD)

    user = build_user(extension)

    user_id = server.users.add(user)
    return int(user_id)


def build_user(extension):
    user = User(firstname='voicemail', lastname='user', language='fr_FR')

    user_line = UserLine(protocol='sip', context='default', number=extension)

    user_voicemail = UserVoicemail(number=extension, name='voicemail user')

    user.line = user_line
    user.voicemail = user_voicemail

    return user


def check_database_tables(user_id, extension):
    connection = psycopg2.connect(host=DB_HOST,
                                  port=DB_PORT,
                                  dbname=DB_NAME,
                                  user=DB_USER,
                                  password=DB_PASSWORD)

    check_voicemail(connection, extension)
    check_userfeatures(connection, user_id)
    check_sccp_device(connection, extension)
    check_usersip(connection, extension)


def check_voicemail(conn, extension):
    query = "SELECT COUNT(*) FROM voicemail WHERE mailbox = %s"
    cursor = conn.cursor()
    cursor.execute(query, (extension,))

    count = cursor.fetchone()[0]

    assert count == 0, "voicemail was not deleted"


def check_userfeatures(conn, user_id):
    query = "SELECT voicemailid FROM userfeatures WHERE id = %s"
    cursor = conn.cursor()
    cursor.execute(query, (user_id,))

    voicemail_id = cursor.fetchone()[0]

    assert voicemail_id is None, "voicemail was not deleted in userfeatures"


def check_sccp_device(conn, extension):
    query = "SELECT COUNT(voicemail) FROM sccpdevice WHERE line = %s AND voicemail != ''"
    cursor = conn.cursor()
    cursor.execute(query, (extension,))

    count = cursor.fetchone()[0]

    assert count == 0, "voicemail was not deleted in sccpdevice"


def check_usersip(conn, extension):
    query = "SELECT COUNT(*) FROM usersip WHERE mailbox = %s"
    cursor = conn.cursor()

    full_extension = '%s@default' % extension
    cursor.execute(query, (full_extension,))

    count = cursor.fetchone()[0]

    assert count == 0, "voicemail was not deleted in usersip"


if __name__ == "__main__":
    extension = '1300'

    print "deleting user and voicemail..."
    delete_user_and_voicemail(extension)

    print "creating user and voicemail..."
    user_id = create_user_and_voicemail(extension)
    #voicemail.delete(extension=extension)

    print "checking database tables..."
    check_database_tables(user_id, extension)
