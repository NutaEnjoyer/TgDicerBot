from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from bot.start_bot_container import bot
from bot_data import config
from db.models import Game, GameInvoice, SecondGameInvoice, User
from . import templates, states
from handlers import utils

from .cryptobot import CryptoBot

def get_title_by_type(type):
	match type:
		case 'dice':
			game_title = "🎲 Игра в кубик"
		case 'darts':
			game_title = "🎯 Игра в дарц"
		case 'bowling':
			game_title = "🎳 Игра в боулинг"
		case _:
			game_title = "ValueError"
	return game_title

async def start_handler(message: types.Message, state: FSMContext):
	await state.finish()
	await bot.delete_message(message.chat.id, message.message_id)

	user = User.get_or_none(user_id=message.from_user.id)
	if not user:
		s = message.get_args()
		if s and s.isdigit():
			ref_id = int(s)
			user = User.get_or_none(user_id=ref_id)
			if user:
				user.referal_count += 1
				user.save()
		else:
			ref_id = None

		user = User.create(user_id=message.from_user.id, i_am_referal_of=ref_id)
		user.save()

	config = utils.get_config()
	await message.answer_sticker(templates.STICKER_ID, reply_markup=templates.menu_keyboard())
	p = await message.from_user.get_profile_photos()
	b = await bot.get_me()
	await message.answer_photo(config.profile_photo, templates.profile_message(user, utils.get_config(), b.username))
	await message.answer(templates.main_message, reply_markup=templates.main_keyboard(config.coefficient))



async def menu_handler(message: types.Message, state: FSMContext):
	await state.finish()
	await bot.delete_message(message.chat.id, message.message_id)
	await message.answer_sticker(templates.STICKER_ID, reply_markup=templates.menu_keyboard())
	config = utils.get_config()

	await message.answer(templates.main_message, reply_markup=templates.main_keyboard(config.coefficient))

async def profile_handler(message: types.Message, state: FSMContext):
	user = User.get_or_none(user_id=message.from_user.id)
	p = await message.from_user.get_profile_photos()
	b = await bot.get_me()

	await message.answer_photo(utils.get_config().profile_photo, templates.profile_message(user, utils.get_config(), b.username))


async def rules_handler(message: types.Message, state: FSMContext):
	p = await message.from_user.get_profile_photos()

	await message.answer_photo(utils.get_config().rules_photo, templates.rules_message())

async def any_handler(message: types.Message, state: FSMContext):
	print(message)

async def dice_handler(call: types.CallbackQuery, state: FSMContext):
	config = utils.get_config()
	await state.set_state(states.Game.Dice)
	await state.update_data(type='dice')
	await call.message.edit_text(templates.dice_message(config.coefficient), reply_markup=templates.game_keyboard())

async def darts_handler(call: types.CallbackQuery, state: FSMContext):
	config = utils.get_config()
	await state.set_state(states.Game.Darts)
	await state.update_data(type='darts')
	await call.message.edit_text(templates.darts_message(config.coefficient), reply_markup=templates.game_keyboard())

async def bowling_handler(call: types.CallbackQuery, state: FSMContext):
	config = utils.get_config()
	await state.set_state(states.Game.Bowling)
	await state.update_data(type='bowling')
	await call.message.edit_text(templates.bowling_message(config.coefficient), reply_markup=templates.game_keyboard())

async def next_game_handler(call: types.CallbackQuery, state: FSMContext):
	config = utils.get_config()
	data = await state.get_data()

	await state.set_state(states.Game.SendPrice)
	game_title = get_title_by_type(data.get('type'))

	mes = await call.message.edit_text(templates.game_send_price(game_title, config.min_bet), reply_markup=templates.only_back())
	await state.update_data(menu_message=mes.message_id)


async def back_game_handler(call: types.CallbackQuery, state: FSMContext):
	await state.finish()
	config = utils.get_config()
	await call.message.edit_text(templates.main_message, reply_markup=templates.main_keyboard(config.coefficient))

async def send_game_price(message: types.Message, state: FSMContext):
	await bot.delete_message(message.chat.id, message.message_id)
	data = await state.get_data()
	game_title = get_title_by_type(data.get('type'))
	config = utils.get_config()

	if not message.text.isdigit():
		await bot.edit_message_text(templates.game_send_price_warn(game_title, config.min_bet), message.chat.id, data.get('menu_message'), reply_markup=templates.only_back())
		return

	price = int(message.text)

	if price < config.min_bet:
		await bot.edit_message_text(templates.game_send_price_warn(game_title, config.min_bet), message.chat.id,
									data.get('menu_message'), reply_markup=templates.only_back())
		return

	await state.update_data(price=price)
	match data.get('type'):
		case 'dice':
			await state.set_state(states.Game.Dice)
		case 'darts':
			await state.set_state(states.Game.Darts)
		case 'bowling':
			await state.set_state(states.Game.Bowling)
	await bot.edit_message_text(templates.choose_payment_method(game_title, price), message.chat.id, data.get('menu_message'),
								reply_markup=templates.choose_payment_method_keyboard())


async def payment_game_handler(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await call.message.edit_text(templates.cryptobot_message(get_title_by_type(data.get('type')), data.get('price')),
								 reply_markup=templates.cryptobot_message_keyboard())

async def payment_next_game_handler(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	print(data)

	config = utils.get_config()
	cryptobot = CryptoBot(config.cryptobot_token)
	invoice = cryptobot.create_invoice(round(data.get('price') * 1.03 / cryptobot.get_usdt_to_rub_course(), 2))

	pay_url = invoice['result']['pay_url']
	invoice_id = invoice['result']['invoice_id']

	game = Game.create(
		type=data.get('type'),
		price=data.get('price'),
		player_1=call.from_user.id
	)
	game.save()

	game_invoice = GameInvoice.create(
		player_id=call.from_user.id,
		game_id=game.id,
		invoice_id=invoice_id,
		message_id=data.get('menu_message')
	)

	game_invoice.save()


	mes = await call.message.edit_reply_markup(reply_markup=templates.payment_form_keyboard(pay_url))


async def edit_message_game_invoice_success(game_invoice_id):
	print(game_invoice_id)
	print('in0')

	game_invoice = GameInvoice.get_or_none(id=game_invoice_id)
	if not game_invoice: return
	print('in1')
	game  = Game.get_or_none(id=game_invoice.game_id)
	if not game: return

	print('in')
	try:
		await bot.edit_message_text(templates.start_game_created_message(game.id, get_title_by_type(game.type),	game.price),
								game_invoice.player_id, game_invoice.message_id)
	except Exception as e:
		print(e)

	await bot.send_message(config.FIND_CHAT_ID, templates.start_game_created_message_for_find(game.id, get_title_by_type(game.type), game.price),
						   reply_markup=templates.start_game_created_message_for_find_keyboard(game.id))

	game_invoice.delete_instance()

async def edit_message_game_invoice_and_find_success(game_invoice_id, find_game: Game):
	game_invoice = GameInvoice.get_or_none(id=game_invoice_id)
	if not game_invoice: return

	find_game.player_2 = game_invoice.player_id
	find_game.save()

	try:
		await bot.delete_message(game_invoice.player_id, game_invoice.message_id)
	except Exception as e:
		print(e)

	await play_game(find_game)

	game_invoice.delete_instance()

async def play_game(game: Game):
	chat_1 = await bot.get_chat(game.player_1)
	chat_2 = await bot.get_chat(game.player_2)
	while not game.winner:
		await bot.send_message(config.PLAY_CHAT_ID, templates.game_start_message(
			game.id,
			get_title_by_type(game.type),
			game.price,
			chat_1,
			chat_2
		))

		match game.type:
			case 'dice':
				mes_1 = await bot.send_dice(config.PLAY_CHAT_ID)
				mes_2 = await bot.send_dice(config.PLAY_CHAT_ID)

				val_1 = mes_1.dice.value
				val_2 = mes_2.dice.value
			case 'darts':
				mes_1 = await bot.send_dice(config.PLAY_CHAT_ID, emoji='🎯')
				mes_2 = await bot.send_dice(config.PLAY_CHAT_ID, emoji='🎯')


				val_1 = mes_1.dice.value
				val_2 = mes_2.dice.value
			case 'bowling':
				mes_1 = await bot.send_dice(config.PLAY_CHAT_ID, emoji='🎳')
				mes_2 = await bot.send_dice(config.PLAY_CHAT_ID, emoji='🎳')

				val_1 = mes_1.dice.value
				val_2 = mes_2.dice.value
			case _:
				val_1 = 1
				val_2 = 2


		if val_1 == val_2:
			continue

		game.winner = game.player_1 if val_1 > val_2 else game.player_2
		game.status = "FINISHED"
		game.save()

	cfg = utils.get_config()
	cryptobot = CryptoBot(cfg.cryptobot_token)

	print("Preparing transfer")
	cryptobot.transfer(game.winner, round(game.price * cfg.coefficient / cryptobot.get_usdt_to_rub_course(), 2))
	print("Transfer finished")
	user_1 = User.get(user_id=game.player_1)
	user_2 = User.get(user_id=game.player_2)

	ref_sum = round(game.price * cfg.referal_rate / 100, 2)
	if user_1.i_am_referal_of:
		user = User.get(user_id=user_1.i_am_referal_of)
		user.referal_sum += ref_sum
		user.referal_balance += ref_sum
		if user.referal_balance >=100:
			cryptobot.transfer(user_1.i_am_referal_of, round(user.referal_balance / cryptobot.get_usdt_to_rub_course(), 2))
			user.referal_balance = 0
		user.save()


	if user_2.i_am_referal_of:
		user = User.get(user_id=user_2.i_am_referal_of)
		user.referal_sum += ref_sum
		user.referal_balance += ref_sum
		if user.referal_balance >= 100:
			cryptobot.transfer(user_2.i_am_referal_of,
							   round(user.referal_balance / cryptobot.get_usdt_to_rub_course(), 2))

			user.referal_balance = 0
		user.save()

	winner_chat = await bot.get_chat(game.winner)

	await bot.send_message(config.PLAY_CHAT_ID, templates.game_end_message(game.id,
			get_title_by_type(game.type),
			game.price,
			chat_1,
			chat_2,
			winner_chat,
			game.price * cfg.coefficient))

	await bot.send_message(game.winner, templates.win_user_game(game.id,
			get_title_by_type(game.type),
				game.price,
			game.price * cfg.coefficient))

	mes = await bot.send_message(game.player_1 if game.winner == game.player_2 else game.player_2, templates.lose_user_game(game.id,
			get_title_by_type(game.type),
			game.price,))
	game.connect_message_id = mes.message_id
	game.save()

async def game_already_started(game_invoice_id):
	game_invoice = SecondGameInvoice.get_or_none(id=game_invoice_id)
	if not game_invoice: return

	await bot.edit_message_text(templates.game_already_started(), game_invoice.player_id, game_invoice.message_id)
	# await bot.delete_message(config.FIND_CHAT_ID, game_invoice.message_id)
	game_invoice.delete_instance()

async def second_game_started(game_invoice_id):
	game_invoice = SecondGameInvoice.get_or_none(id=game_invoice_id)
	if not game_invoice: return

	game = Game.get(id=game_invoice.game_id)
	await play_game(game)
	await bot.delete_message(config.FIND_CHAT_ID, game_invoice.chat_message_id)

async def connect_to_game_handler(call: types.CallbackQuery, state: FSMContext):
	game = Game.get_or_none(id=int(call.data.split('$')[1]))
	if not game:
		await call.message.delete()
		await bot.answer_callback_query(call.id, 'Игра завершена!')
	if game.status != "PAID":
		await call.message.delete()
		await bot.answer_callback_query(call.id, 'Игра завершена!')
	config = utils.get_config()
	cryptobot = CryptoBot(config.cryptobot_token)
	invoice = cryptobot.create_invoice(round(game.price * 1.03 / cryptobot.get_usdt_to_rub_course(), 2))

	pay_url = invoice['result']['pay_url']
	invoice_id = invoice['result']['invoice_id']

	game_invoice = SecondGameInvoice.create(
		player_id=call.from_user.id,
		game_id=game.id,
		invoice_id=invoice_id,
		message_id=None,
		chat_message_id=call.message.message_id
	)
	mes = await bot.send_message(call.from_user.id, templates.cryptobot_message(get_title_by_type(game.type), game.price),
						   reply_markup=templates.second_payment_form_keyboard(pay_url))
	game_invoice.message_id = mes.message_id
	game_invoice.save()

	await bot.answer_callback_query(call.id, templates.call_answer_connect)


async def admin_handler(message: types.Message, state: FSMContext):
	await message.answer(templates.admin_message(), reply_markup=templates.admin_menu())

async def back_and_finish_handler(call: types.CallbackQuery, state: FSMContext):
	await call.message.delete()
	await state.finish()

async def edit_min_bet(call: types.CallbackQuery, state: FSMContext):
	await state.set_state(states.Admin.MinBet)
	c = utils.get_config()
	m = await call.message.answer(templates.send_new(c.min_bet), reply_markup=templates.only_back_menu())
	await state.update_data(delete_it=m.message_id)

async def edit_coefficient(call: types.CallbackQuery, state: FSMContext):
	await state.set_state(states.Admin.Coefficien)
	c = utils.get_config()
	m = await call.message.answer(templates.send_new(c.coefficient), reply_markup=templates.only_back_menu())
	await state.update_data(delete_it=m.message_id)

async def edit_cryptobot_token(call: types.CallbackQuery, state: FSMContext):
	await state.set_state(states.Admin.CryptobotToken)
	c = utils.get_config()
	m = await call.message.answer(templates.send_new(c.cryptobot_token), reply_markup=templates.only_back_menu())
	await state.update_data(delete_it=m.message_id)

async def edit_referal_rate(call: types.CallbackQuery, state: FSMContext):
	await state.set_state(states.Admin.ReferalRate)
	c = utils.get_config()
	m = await call.message.answer(templates.send_new(c.referal_rate), reply_markup=templates.only_back_menu())
	await state.update_data(delete_it=m.message_id)

async def send_edit_min_bet(message: types.Message, state: FSMContext):
	data = await state.get_data()
	await state.finish()

	c = utils.get_config()
	c.min_bet = int(message.text)
	c.save()

	await bot.delete_message(message.chat.id, message.message_id)
	await bot.delete_message(message.chat.id, data.get('delete_it'))

async def send_edit_coefficient(message: types.Message, state: FSMContext):
	data = await state.get_data()
	await state.finish()

	c = utils.get_config()
	c.coefficient = float(message.text)
	c.save()

	await bot.delete_message(message.chat.id, message.message_id)
	await bot.delete_message(message.chat.id, data.get('delete_it'))

async def send_edit_cryptobot_token(message: types.Message, state: FSMContext):
	data = await state.get_data()
	await state.finish()

	c = utils.get_config()
	c.cryptobot_token = message.text
	c.save()

	await bot.delete_message(message.chat.id, message.message_id)
	await bot.delete_message(message.chat.id, data.get('delete_it'))

async def send_edit_referal_rate(message: types.Message, state: FSMContext):
	data = await state.get_data()
	await state.finish()

	c = utils.get_config()
	c.referal_rate = int(message.text)
	c.save()

	await bot.delete_message(message.chat.id, message.message_id)
	await bot.delete_message(message.chat.id, data.get('delete_it'))

async def edit_profile_photo(call: types.CallbackQuery, state: FSMContext):
	await state.set_state(states.Admin.ProfilePhoto)
	c = utils.get_config()
	m = await call.message.answer(templates.send_new(c.profile_photo), reply_markup=templates.only_back_menu())
	await state.update_data(delete_it=m.message_id)


async def edit_rules_photo(call: types.CallbackQuery, state: FSMContext):
	await state.set_state(states.Admin.RulesPhoto)
	c = utils.get_config()
	m = await call.message.answer(templates.send_new(c.rules_photo), reply_markup=templates.only_back_menu())
	await state.update_data(delete_it=m.message_id)

async def send_edit_profile_photo(message: types.Message, state: FSMContext):
	data = await state.get_data()
	await state.finish()

	c = utils.get_config()
	c.profile_photo = message.photo[-1].file_id
	c.save()

	await bot.delete_message(message.chat.id, message.message_id)
	await bot.delete_message(message.chat.id, data.get('delete_it'))

async def send_edit_rules_photo(message: types.Message, state: FSMContext):
	data = await state.get_data()
	await state.finish()

	c = utils.get_config()
	c.rules_photo = message.photo[-1].file_id
	c.save()

	await bot.delete_message(message.chat.id, message.message_id)
	await bot.delete_message(message.chat.id, data.get('delete_it'))

def register_handlers(dp: Dispatcher):
	dp.register_message_handler(start_handler, commands=['start', 'restart'], state='*')
	dp.register_message_handler(admin_handler, commands=['admin'], state='*')
	dp.register_message_handler(menu_handler, text=templates.menu_button, state='*')
	dp.register_message_handler(profile_handler, text=templates.profile_button, state='*')
	dp.register_message_handler(rules_handler, text=templates.rules_button, state='*')

	dp.register_callback_query_handler(dice_handler, text='dice', state='*')
	dp.register_callback_query_handler(darts_handler, text='darts', state='*')
	dp.register_callback_query_handler(bowling_handler, text='bowling', state='*')

	dp.register_callback_query_handler(next_game_handler, text='next', state=states.Game)
	dp.register_callback_query_handler(back_game_handler, text='back', state=states.Game)

	dp.register_callback_query_handler(payment_game_handler, text='payment', state=states.Game)
	dp.register_callback_query_handler(payment_next_game_handler, text='next_payment', state=states.Game)

	dp.register_callback_query_handler(connect_to_game_handler, text_startswith='connect_to_game', state="*")
	dp.register_callback_query_handler(back_and_finish_handler, text='back_and_finish', state="*")

	dp.register_message_handler(send_game_price, content_types=['text'], state=states.Game.SendPrice)

	# dp.register_pre_checkout_query_handler(proccess_pre_checkout_query)

	dp.register_callback_query_handler(edit_min_bet, text='edit_min_bet', state="*")
	dp.register_callback_query_handler(edit_coefficient, text='edit_coefficient', state="*")
	dp.register_callback_query_handler(edit_cryptobot_token, text='edit_cryptobot_token', state="*")
	dp.register_callback_query_handler(edit_referal_rate, text='edit_referal_rate', state="*")
	dp.register_callback_query_handler(edit_profile_photo, text='edit_profile_photo', state="*")
	dp.register_callback_query_handler(edit_rules_photo, text='edit_rules_photo', state="*")

	dp.register_message_handler(send_edit_min_bet, content_types=['text'], state=states.Admin.MinBet)
	dp.register_message_handler(send_edit_coefficient, content_types=['text'], state=states.Admin.Coefficien)
	dp.register_message_handler(send_edit_cryptobot_token, content_types=['text'], state=states.Admin.CryptobotToken)
	dp.register_message_handler(send_edit_referal_rate, content_types=['text'], state=states.Admin.ReferalRate)
	dp.register_message_handler(send_edit_profile_photo, content_types=['photo'], state=states.Admin.ProfilePhoto)
	dp.register_message_handler(send_edit_rules_photo, content_types=['rules'], state=states.Admin.RulesPhoto)


	dp.register_message_handler(any_handler, content_types=types.ContentTypes.ANY, state='*')
