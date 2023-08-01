echo "Установка Листочка 0.2dev1 (версия установщика 0.1dev1)"

./deploy/install-apt-deps &&
./deploy/install-python311 &&
./deploy/install-python311-venv "$PWD" &&
./deploy/install-postgres15 &&

echo "Процедура установки успешно завершилась."
