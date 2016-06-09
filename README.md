xivo-dao [![Build Status](https://travis-ci.org/xivo-pbx/xivo-dao.png?branch=master)](https://travis-ci.org/xivo-pbx/xivo-dao)
========

xivo-dao is a library used internally by XiVO to access and modify
different data sources (e.g. postgres database, provisoning database).

Creating the test database
--------------------------

```
apt-get install postgres-9.4
sudo -u postgres psql
```

Then:

```
CREATE DATABASE asterisktest;
CREATE USER asterisk WITH PASSWORD 'asterisk';
GRANT ALL ON DATABASE asterisktest TO asterisk;
```

Running unit tests
------------------

You need the test database ``asterisktest`` installed (see above).

```
apt-get install libpq-dev python-dev libyaml-dev
pip install tox
tox --recreate -e py27
```

To execute tests slightly faster, you can avoid recreating all the tables in the
database by passing ```CREATE_TABLES=0``` on the command line


Docker
------

To run test with docker:

    docker build -t xivo/dao-test .
    docker run -e XIVO_TEST_DB_URL=<postgres_uri> -it xivo/dao bash

To run with docker-compose:

    docker-compose up -d db  # only once
    # wait a bit
    docker-compose build dao && docker-compose up dao  # repeat to run against new code
