from peewee import *
from bot_data import config
import time
import datetime

def current_date():
	months = ['Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня', 'Июля', 'Августа', 'Сентября', 'Октября', 'Ноября', 'Декабря']
	now = datetime.datetime.now()
	month = months[now.month - 1]
	date_str = now.strftime('%H:%M %d ') + month + now.strftime(' %Y')
	return date_str

database = SqliteDatabase('database.db')

class BaseModel(Model):
	id = PrimaryKeyField()

	class Meta:
		database = database


class Config(BaseModel):
	min_bet = IntegerField(default=100)
	coefficient = FloatField(default=1.8)
	cryptobot_token = CharField(default=config.CRYPTOBOT_TOKEN)
	referal_rate = IntegerField(default=10)
	profile_photo = CharField(null=True)
	rules_photo = CharField(null=True)


class Game(BaseModel):
	type = CharField()  # dice darts bowling
	price = IntegerField()  # PRICE OF THE GAME
	player_1 = IntegerField() # OWNER ID
	player_2 = IntegerField(null=True) # SECOND PLAYER ID
	winner = IntegerField(null=True) # WINNER ID

	created_at = IntegerField(default=time.time)
	status = CharField(default="CREATED")  # CREATED PAID FINISHED

	connect_message_id = IntegerField(null=True)


class GameInvoice(BaseModel):
	player_id = IntegerField()
	message_id = IntegerField()
	game_id = IntegerField()
	invoice_id = IntegerField()

	created_at = IntegerField(default=time.time)

class SecondGameInvoice(BaseModel):
	player_id = IntegerField()
	message_id = IntegerField(null=True)
	chat_message_id = IntegerField()
	game_id = IntegerField()
	invoice_id = IntegerField()

	created_at = IntegerField(default=time.time)


class User(BaseModel):
	user_id = IntegerField()
	register_date = CharField(default=current_date)
	deposite_sum = IntegerField(default=0)
	referal_count = IntegerField(default=0)
	referal_sum = IntegerField(default=0)
	i_am_referal_of = IntegerField(null=True)
	referal_balance = IntegerField(default=0)


def main():
	database.drop_tables([Config])
	database.create_tables([Config])
	# database.create_tables([User])


if __name__ == "__main__":
	main()

