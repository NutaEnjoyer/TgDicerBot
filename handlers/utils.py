from db.models import Config, Game
from peewee import DoesNotExist


def get_config() -> Config:
	try:
		last_config = Config.select().order_by(Config.id.desc()).get()
		return last_config
	except DoesNotExist:
		c = Config.create()
		c.save()
		return c


def find_game_for_me(player_1, type, price):
	print(f'Find game for me: {type=} {price=}')
	games = list(Game.select().where(
		(Game.type==type) & (Game.price == price) & (Game.status == "PAID") & (Game.player_2==None) & ~(Game.player_1==player_1)
	).order_by(Game.created_at))
	if games: return games[0]
