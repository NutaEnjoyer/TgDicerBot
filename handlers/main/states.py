from aiogram.dispatcher.filters.state import State, StatesGroup

class Game(StatesGroup):
	Dice = State()
	Darts = State()
	Bowling = State()
	SendPrice = State()

class Admin(StatesGroup):
	MinBet = State()
	Coefficien = State()
	CryptobotToken = State()
	ReferalRate = State()
	ProfilePhoto = State()
	RulesPhoto = State()


