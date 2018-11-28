xivo-dao [![Build Status](https://jenkins.wazo.community/buildStatus/icon?job=xivo-dao)](https://jenkins.wazo.community/job/xivo-dao)
========

xivo-dao is a library used internally by Wazo to access and modify
different data sources (e.g. postgres database, provisoning database).

Creating the test database
--------------------------

```
apt-get install postgres postgresql-contrib
sudo -u postgres psql
```

Then:

```
CREATE USER asterisk WITH PASSWORD 'asterisk';
CREATE DATABASE asterisktest OWNER asterisk;
\c asterisktest
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

Running unit tests
------------------

You need the test database ``asterisktest`` installed (see above).

```
apt-get install libpq-dev python-dev libyaml-dev python3.5-dev
pip install tox
tox --recreate -e py27,py35
```

To execute tests slightly faster, you can avoid recreating all the tables in the
database by passing ```CREATE_TABLES=0``` on the command line


Docker
------

Start the database (needed only once):

    docker-compose up -d db
    export XIVO_TEST_DB_URL=postgresql://asterisk:proformatique@$(docker-compose port db 5432)/asterisk

Run your tests:

    nosetests -x xivo_dao

OR

    docker-compose build dao && docker-compose up dao
