from debian:jessie

RUN apt-get -yqq update \
    && apt-get -yqq install python-pip \
                            git \
                            libpq-dev \
                            python-dev \
                            libyaml-dev

ADD . /usr/src/dao
WORKDIR /usr/src/dao
RUN pip install -r requirements.txt
RUN pip install -r test-requirements.txt

CMD nosetests xivo_dao
