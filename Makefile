#################
#  Makefile     #
#################

# Первая настройка бота
bot_setup:
	pip install -r requirements.txt

# Применить миграции
db_migrate:
	orator migrate -c tgbot/db/connect.py -p tgbot/db/migrations -f

# Откатить миграции
db_rollback:
	orator migrate:rollback -c tgbot/db/connect.py -p tgbot/db/migrations -f

# Сиды (тестовые данные)
db_seed:
	orator db:seed --config tgbot/db/connect.py -p tgbot/db/seeds -f




