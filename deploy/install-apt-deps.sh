#!/bin/bash

if [ "$EUID" -ne 0 ]
then 
    echo "Для запуска требуются права суперпользователя."
    exit -1
fi

echo "Стадия 1: установка зависимостей компиляции"

if command -v apt >/dev/null 2>&1; 
then
    apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev liblzma-dev tk-dev
else
    echo "apt недоступен. Пытаюсь получить пакеты из apt-get..."
    apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev liblzma-dev tk-dev
fi
