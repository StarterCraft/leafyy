#!/bin/bash

if [ "$EUID" -ne 0 ]
then
    echo "Для запуска требуются права суперпользователя."
    exit -1
fi

echo "Стадия 2: установка Python 3.11.4"

if command -v python3.11 &> /dev/null
then
    cd /tmp/
    wget https://www.python.org/ftp/python/3.11.4/Python-3.11.4.tgz
    tar xzf Python-3.11.4.tgz
    cd Python-3.11.4

    ./configure --prefix=/usr/bin/python/3.11.4/ --enable-optimizations --with-lto --with-computed-gotos --with-system-ffi
    make -j "$(nproc)"
    make altinstall
    rm /tmp/Python-3.11.4.tgz

    /usr/bin/python/3.11.4/bin/python3.11 -m pip install --upgrade pip setuptools wheel

    ln -s /usr/bin/python/3.11.4/bin/python3.11        /usr/bin/python/3.11.4/bin/python3
    ln -s /usr/bin/python/3.11.4/bin/python3.11        /usr/bin/python/3.11.4/bin/python
    ln -s /usr/bin/python/3.11.4/bin/pip3.11           /usr/bin/python/3.11.4/bin/pip3
    ln -s /usr/bin/python/3.11.4/bin/pip3.11           /usr/bin/python/3.11.4/bin/pip
    ln -s /usr/bin/python/3.11.4/bin/pydoc3.11         /usr/bin/python/3.11.4/bin/pydoc
    ln -s /usr/bin/python/3.11.4/bin/idle3.11          /usr/bin/python/3.11.4/bin/idle
    ln -s /usr/bin/python/3.11.4/bin/python3.11-config      /usr/bin/python/3.11.4/bin/python-config
else
    echo "Python 3.11.4 уже установлен, пропускаю..."
fi
