import datetime
import time
from pprint import pprint

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram.utils import executor
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from bot_data import config

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.start_bot_container import bot
from db.models import Game, GameInvoice, SecondGameInvoice, User
from handlers.main.cryptobot import CryptoBot
from handlers.main.main import edit_message_game_invoice_success, edit_message_game_invoice_and_find_success, \
	second_game_started, game_already_started
from handlers.utils import get_config, find_game_for_me


scheduler = AsyncIOScheduler()

dp = Dispatcher(bot, storage=MemoryStorage())


def delete_games_and_game_invoices():
	games = Game.select().where(
		(Game.created_at < time.time() - config.TIME_GAME_LIVE * 60) &
		(Game.status=="PAID")
	)

	for game in games:
		cfg = get_config()
		cryptobot = CryptoBot(cfg.cryptobot_token)
		cryptobot.transfer(game.player_1, game.price)
		game.delete_instance()

	game_invoices = GameInvoice.select().where(GameInvoice.created_at < time.time() - config.TIME_INVOICE_LIVE * 60)

	for game_invoice in game_invoices:
		game = Game.get_or_none(id=game_invoice.game_id)
		if game:
			game.delete_instance()
		game_invoice.delete_instance()

	game_invoices = SecondGameInvoice.select().where(SecondGameInvoice.created_at < time.time() - config.TIME_INVOICE_LIVE * 60)

	for game_invoice in game_invoices:
		game_invoice.delete_instance()



async def check_invoices():
	game_invoices = GameInvoice.select()
	for game_invoice in game_invoices:
		print(game_invoice.id)
		cfg = get_config()
		cryptobot = CryptoBot(cfg.cryptobot_token)
		if not cryptobot.check_invoice(game_invoice.invoice_id):
			continue

		game = Game.get_or_none(id=game_invoice.game_id)
		if not game: continue
		game.status = "PAID"
		game.save()

		user = User.get_or_none(user_id=game_invoice.player_id)
		if not user:
			user = User.create(user_id=game_invoice.player_id)
			user.save()

		user.deposite_sum += game.price
		user.save()

		find_game = find_game_for_me(game.player_1, game.type, game.price)
		if not find_game:
			print('this block')
			await edit_message_game_invoice_success(game_invoice.id)
		else:
			print('that block')
			game.delete_instance()
			await edit_message_game_invoice_and_find_success(game_invoice.id, find_game)


async def check_second_invoices():
	game_invoices = SecondGameInvoice.select()
	for game_invoice in game_invoices:
		print(game_invoice.id)
		cfg = get_config()
		cryptobot = CryptoBot(cfg.cryptobot_token)
		if not cryptobot.check_invoice(game_invoice.invoice_id):
			continue

		game = Game.get(id=game_invoice.game_id)
		user = User.get_or_none(user_id=game_invoice.player_id)
		if not user:
			user = User.create(user_id=game_invoice.player_id)
			user.save()

		user.deposite_sum += game.price
		user.save()
		if game.player_2:
			cryptobot.transfer(game_invoice.player_id, game.price)
			await game_already_started(game_invoice.id)
		else:
			game.player_2 = game_invoice.player_id
			game.save()
			await second_game_started(game_invoice.id)


async def do_some():
	delete_games_and_game_invoices()
	await check_invoices()
	await check_second_invoices()

def schedule_job():
	scheduler.add_job(do_some, 'interval', seconds=10)


async def __on_start_up(dp: Dispatcher) -> None:
	from handlers import register_all_handlers

	register_all_handlers.register(dp)

	schedule_job()


def start_bot():
	scheduler.start()
	executor.start_polling(dp, skip_updates=True, on_startup=__on_start_up)
