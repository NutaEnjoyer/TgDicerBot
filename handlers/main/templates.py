from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from db.models import User, Config

STICKER_ID = "CAACAgIAAxkBAAICk2YAAX22DVAUaEPBQsNag1OfxsY8IQACIAkAAhhC7gjhiiCooToK2TQE"

main_message = """<b>🎮 Доступные игры</b>

<i>Выберите игру, в которую вы хотите сыграть</i>"""

menu_button = "🎮 Меню"
profile_button = "👤 Профиль"
rules_button = "📘Правила"

def main_keyboard(coefficient: int = 1.8):
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[InlineKeyboardButton(f"🎲 Кубик ({coefficient}x)", callback_data='dice')],
			[InlineKeyboardButton(f"🎯 Дартс ({coefficient}x)", callback_data='darts')],
			[InlineKeyboardButton(f"🎳 Боулинг ({coefficient}x)", callback_data='bowling')],
		]
	)

def menu_keyboard():
	return ReplyKeyboardMarkup(
		resize_keyboard=True,
		keyboard=[
			[KeyboardButton(menu_button)],
			[KeyboardButton(profile_button), KeyboardButton(rules_button)],
		]
	)

def dice_message(coefficient: int):
	return f"""<b>🎲 Игра в кубик</b>

Игра идет автоматически между двумя людьми. Бот кидает кубики, человек с большей цифрой на кубике получает сумму, умноженную на коэффициент!

Коэффициент: {coefficient}x"""

def darts_message(coefficient: int):
	return f"""<b>🎲 Игра в дарц</b>

Игра идет автоматически между двумя людьми. Бот кидает 2 эмоджи дарц, человек с большим количеством очков получает сумму, умноженную на коэффициент!

Коэффициент: {coefficient}x"""

def bowling_message(coefficient: int):
	return f"""<b>🎲 Игра в боулинг</b>

Игра идет автоматически между двумя людьми. Бот кидает 2 эмоджи боулинг, человек с большим количеством очков получает сумму, умноженную на коэффициент!

Коэффициент: {coefficient}x"""

def game_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[InlineKeyboardButton("Продолжить >", callback_data='next')],
			[InlineKeyboardButton("< Назад", callback_data='back')],
		]
	)

def only_back():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[InlineKeyboardButton("< Назад", callback_data='back')],
		]
	)


def game_send_price(title, min_price):
	return f"""<b>{title}</b>

Минимальная сумма: <b>{min_price} RUB</b>

<i>Введите сумму ставки в <b>RUB</b></i>"""

def game_send_price_warn(title, min_price):
	return f"""<b>{title}</b>

Минимальная сумма: <b>{min_price} RUB</b>

<i>Введите сумму ставки в <b>RUB</b></i>

<b>Укажите корректную сумму!</b>"""


def choose_payment_method(title, price):
	return f"""<b>{title}</b>
	
Сумма ставки: <b>{price} RUB</b>

<i>Выберите метод оплаты ставки</i>"""

def choose_payment_method_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[InlineKeyboardButton("👛 CryptoBot (3%)", callback_data='payment')],
			[InlineKeyboardButton("< Назад", callback_data='back')],
		]
	)


def cryptobot_message(title, price):
	return f"""<b>{title}</b>

Сумма ставки: <b>{price} RUB</b>
Метод оплаты: <b>CryptoBot</b>

<i>Нажмите на кнопку «Продолжить», чтобы создать ставку</i>"""


def cryptobot_message_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[InlineKeyboardButton("Продолжить >", callback_data='next_payment')],
			[InlineKeyboardButton("< Назад", callback_data='back')],
		]
	)

def payment_form_keyboard(link):
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[InlineKeyboardButton("Оплатить счет", url=link)],
			[InlineKeyboardButton("< Назад", callback_data='back')],
		]
	)

def second_payment_form_keyboard(link):
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[InlineKeyboardButton("Оплатить счет", url=link)],
		]
	)

def game_start_message(game_id, title, price, chat_1, chat_2):
	return f"""<i>🎮 Игра #{game_id} в <b>{title}</b> на сумму <b>{price}.0 RUB</b>, от игроков <a href="{chat_1.user_url}">{chat_1.first_name}</a> и <a href="{chat_2.user_url}">{chat_2.first_name}</a> начинается...
	
<a href="https://t.me/+gNpetsphgwdiMDBi">⚡️Посмотреть игру</a></i>"""

def game_end_message(game_id, title, price, chat_1, chat_2, winner, win_price):
	return f"""
<i>🎮 Игра #{game_id} в <b>{title}</b> на сумму <b>{price}.0 RUB</b>, от игроков <a href="{chat_1.user_url}">{chat_1.first_name}</a> и <a href="{chat_2.user_url}">{chat_2.first_name}</a> завершенна

Победитель: <a href="{winner.user_url}">{winner.first_name}</a>

Суммы выигрыша: <b>{win_price}</b>RUB</i>"""

def lose_user_game(game_id, title, price):
	return f"""<i>🎮 Игра #{game_id} в <b>{title}</b> на сумму <b>{price}.0 RUB</b>, к сожалению была проиграна!</i>"""


def win_user_game(game_id, title, price, win_price):
	return f"""<i>🎮 Игра #{game_id} в <b>{title}</b> на сумму <b>{price}.0 RUB</b>, была выиграна!

Суммы выигрыша: <b>{win_price}</b>RUB</i>"""

def start_game_created_message(game_id, title, price):
	return f"""<i>🎮 Игра #{game_id} в <b>{title}</b> на сумму <b>{price}.0 RUB</b>, создана! Ищем противника!</i>"""

def start_game_created_message_for_find(game_id, title, price):
	return f"""<i>🎮 Игра #{game_id} в <b>{title}</b> на сумму <b>{price}.0 RUB</b>, создана! Ищем противника!</i>"""

def start_game_created_message_for_find_keyboard(game_id):
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[InlineKeyboardButton('Присоединиться', callback_data=f'connect_to_game${game_id}')]
		]
	)

def game_already_started():
	return """<i>К сожалению игра уже заполнена! Средства возвращены вам на баланс!</i>"""


def profile_message(user: User, config: Config, bot_link):

	return f"""<b>📕ID:</b> {user.user_id}

<b>💰Сумма депозитов:</b> {user.deposite_sum} RUB

<b>📅Дата регистрации:</b> {user.register_date}

➖➖➖➖➖➖➖➖➖➖➖➖

<b>📊 Статистика партнерской программы</b>

<b>👤 Кол-во рефералов:</b> {user.referal_count}

<b>📈 Твой процент:</b> {config.referal_rate} %
 
<b>💸 Баланс:</b> {user.referal_balance}

<b>💸 Прибыль:</b> {user.referal_sum}

<b>🔗 Ваша реферальная ссылка:</b> https://t.me/{bot_link}?start={user.user_id}"""


def rules_message():
	return """<b>📕Актуальные правила пользования GameMoney</b>

1) <b>⚡️Как начать игру</b>: нажмите на кнопку <b>«🎮Игры»</b>, выберите игру, укажите сумму, оплатите с помощью CryptoBot, соперник найдется автоматически. Процесс игры можно отслеживать как в боте, так и в нашем чате. 

2) Игра ведётся между двумя людьми.

3) Вы можете присоединиться к доступному набору к игре в нашем чате.

4) Выплаты моментальны на Cryptobot

5)  Активные игры можно посмотреть в категории «🎮Игры» ➡️ «🕐Активные игры».

6) Поддержка GameMoney: @Линканет."""

call_answer_connect = """Сообщение пришло в личные сообщения"""

def admin_menu():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[InlineKeyboardButton('Изменить минимальный депозит', callback_data='edit_min_bet')],
			[InlineKeyboardButton('Изменить коэффициент игры', callback_data='edit_coefficient')],
			[InlineKeyboardButton('Изменить токен крипто бота', callback_data='edit_cryptobot_token')],
			[InlineKeyboardButton('Изменить реферальный процент', callback_data='edit_referal_rate')],
			[InlineKeyboardButton('Изменить профиль фото', callback_data='edit_profile_photo')],
			[InlineKeyboardButton('Изменить правило фото', callback_data='edit_rules_photo')],
		]
	)

def only_back_menu():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[InlineKeyboardButton('Отмена', callback_data='back_and_finish')]
		]
	)

def send_new(old_value):
	return f"""Введите новое значение
	
Текущее значение значение: <code>{old_value}</code>"""

def admin_message():
	return """Вы зашли в админ меню!"""
