from __future__ import unicode_literals

from xivo_ws import XivoServer, User, UserLine, UserVoicemail

from xivo_dao.services import voicemail

import psycopg2

WS_IP = '10.42.0.1'
WS_USERNAME = 'admin'
WS_PASSWORD = 'proformatique'

DB_HOST = '10.42.0.1'
DB_PORT = '5432'
DB_NAME = 'asterisk'
DB_USER = 'asterisk'
DB_PASSWORD = 'proformatique'


def delete_user_and_voicemail(number):
    server = XivoServer(WS_IP, WS_USERNAME, WS_PASSWORD)
    users = server.users.search(number)

    for user in users:
        if user.voicemail:
            server.voicemails.delete(user.voicemail.id)
        server.users.delete(user.id)


def create_user_and_voicemail(number):
    server = XivoServer(WS_IP, WS_USERNAME, WS_PASSWORD)

    user = build_user(number)

    user_id = server.users.add(user)
    return int(user_id)


def build_user(number):
    user = User(firstname='voicemail', lastname='user', language='fr_FR')

    user_line = UserLine(protocol='sip', context='default', number=number)

    user_voicemail = UserVoicemail(number=number, name='voicemail user')

    user.line = user_line
    user.voicemail = user_voicemail

    return user


def check_database_tables(user_id, number):
    connection = psycopg2.connect(host=DB_HOST,
                                  port=DB_PORT,
                                  dbname=DB_NAME,
                                  user=DB_USER,
                                  password=DB_PASSWORD)

    check_voicemail(connection, number)
    check_userfeatures(connection, user_id)
    check_sccp_device(connection, number)
    check_usersip(connection, number)


def check_voicemail(conn, number):
    query = "SELECT COUNT(*) FROM voicemail WHERE mailbox = %s"
    cursor = conn.cursor()
    cursor.execute(query, (number,))

    count = cursor.fetchone()[0]

    assert count == 0, "voicemail was not deleted"


def check_userfeatures(conn, user_id):
    query = "SELECT voicemailid FROM userfeatures WHERE id = %s"
    cursor = conn.cursor()
    cursor.execute(query, (user_id,))

    voicemail_id = cursor.fetchone()[0]

    assert voicemail_id is None, "voicemail was not deleted in userfeatures"


def check_sccp_device(conn, number):
    query = "SELECT COUNT(voicemail) FROM sccpdevice WHERE line = %s AND voicemail != ''"
    cursor = conn.cursor()
    cursor.execute(query, (number,))

    count = cursor.fetchone()[0]

    assert count == 0, "voicemail was not deleted in sccpdevice"


def check_usersip(conn, number):
    query = "SELECT COUNT(*) FROM usersip WHERE mailbox = %s"
    cursor = conn.cursor()

    full_number = '%s@default' % number
    cursor.execute(query, (full_number,))

    count = cursor.fetchone()[0]

    assert count == 0, "voicemail was not deleted in usersip"


if __name__ == "__main__":
    number = '1300'

    print "deleting user and voicemail..."
    delete_user_and_voicemail(number)

    print "creating user and voicemail..."
    user_id = create_user_and_voicemail(number)
    voicemail.delete(number=number)

    print "checking database tables..."
    check_database_tables(user_id, number)
