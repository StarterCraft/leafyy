#!/bin/bash

if [ "$EUID" -ne 0 ]
then
    echo "Для запуска требуются права суперпользователя."
    exit -1
fi

echo "Стадия 3: установка виртуального окружения"

cd $1

if [ ! -d "venv" ]; then
    echo "Создание виртульного окружения..."
    python3.11 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "Виртуальное окружение уже развёрнуто."
    source venv/bin/activate
fi
