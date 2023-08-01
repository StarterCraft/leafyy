#!/bin/bash

if [ "$EUID" -ne 0 ]
then
    echo "Для запуска требуются права суперпользователя."
    exit -1
fi

if ! command -v psql &> /dev/null
then
    echo "Стадия 4: установка PostgreSQL 15.3"

    cd /tmp/
    wget https://ftp.postgresql.org/pub/source/v15.3/postgresql-15.3.tar.gz
    tar xzf postgresql-15.3.tar.gz
    cd postgresql-15.3

    ./configure
    make
    make install
    adduser postgres
    mkdir -p /usr/local/pgsql/data
    chown postgres /usr/local/pgsql/data
    su - postgres
    /usr/local/pgsql/bin/initdb -D /usr/local/pgsql/data
    /usr/local/pgsql/bin/pg_ctl -D /usr/local/pgsql/data -l logfile start
    /usr/local/pgsql/bin/createdb leafyy
    /usr/local/pgsql/bin/psql leafyy
else
    echo "PostgreSQL 15.3 уже установлен, пропускаю..."
fi
