xivo-dao [![Build Status](https://travis-ci.org/wazo-pbx/xivo-dao.png?branch=master)](https://travis-ci.org/wazo-pbx/xivo-dao)
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
apt-get install libpq-dev python-dev libyaml-dev python3.4-dev
pip install tox
tox --recreate -e py27,py34
```

To execute tests slightly faster, you can avoid recreating all the tables in the
database by passing ```CREATE_TABLES=0``` on the command line


Docker
------

To run test with docker:

    docker build -t wazopbx/dao-test .
    docker run -e XIVO_TEST_DB_URL=<postgres_uri> -it wazopbx/dao-test bash

To run with docker-compose:

    docker-compose up -d db  # only once
    # wait a bit
    docker-compose build dao && docker-compose up dao  # repeat to run against new code
