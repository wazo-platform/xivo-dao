xivo-dao [![Build Status](https://travis-ci.org/xivo-pbx/xivo-dao.png?branch=master)](https://travis-ci.org/xivo-pbx/xivo-dao)
========

xivo-dao is a library used internally by XiVO to access and modify
different data sources (e.g. postgres database, provisoning database).

Running unit tests
==================

1. Install PostgreSQL
2. Install dependencies with ```pip install -r requirements.txt```
3. Create a test database
4. Run the tests with ```nosetests xivo_dao```

To execute tests slightly faster, you can avoid recreating all the tables in the
database by passing ```CREATE_TABLES=0``` on the command line

Creating the test database
--------------------------

You can create the database by running these SQL commands:

    CREATE DATABASE asterisktest;
    CREATE USER asterisk WITH PASSWORD 'asterisk';
    GRANT ALL ON DATABASE asterisktest TO asterisk;

On debian based systems you can access the psql console with ```sudo -u postgres psql```

Docker
------

To run test with docker:

    docker build -t xivo/dao-test .
    docker run -e XIVO_TEST_DB_URL=<postgres_uri> -it xivo/dao bash

To run with docker-compose:

    docker-compose up
